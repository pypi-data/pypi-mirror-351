import torch
import torch.nn.functional as F
import time

def compute_iou(preds, targets, threshold=0.5):
    B, _, H, W = preds.shape
    preds = preds.permute(0, 2, 3, 1).reshape(-1, 4)
    targets = targets.permute(0, 2, 3, 1).reshape(-1, 4)

    pred_x1 = preds[:, 0] - preds[:, 2] / 2
    pred_y1 = preds[:, 1] - preds[:, 3] / 2
    pred_x2 = preds[:, 0] + preds[:, 2] / 2
    pred_y2 = preds[:, 1] + preds[:, 3] / 2

    targ_x1 = targets[:, 0] - targets[:, 2] / 2
    targ_y1 = targets[:, 1] - targets[:, 3] / 2
    targ_x2 = targets[:, 0] + targets[:, 2] / 2
    targ_y2 = targets[:, 1] + targets[:, 3] / 2

    inter_x1 = torch.max(pred_x1, targ_x1)
    inter_y1 = torch.max(pred_y1, targ_y1)
    inter_x2 = torch.min(pred_x2, targ_x2)
    inter_y2 = torch.min(pred_y2, targ_y2)

    inter_area = (inter_x2 - inter_x1).clamp(0) * (inter_y2 - inter_y1).clamp(0)
    pred_area = (pred_x2 - pred_x1).clamp(0) * (pred_y2 - pred_y1).clamp(0)
    targ_area = (targ_x2 - targ_x1).clamp(0) * (targ_y2 - targ_y1).clamp(0)

    union_area = pred_area + targ_area - inter_area + 1e-6
    iou = inter_area / union_area
    return (iou > threshold).float().mean().item()

def format_time(seconds: float) -> str:
    return f"{seconds:.1f}s"

def smooth_ema(old, new, alpha=0.1):
    return new if old is None else old * (1 - alpha) + new * alpha

def train_detection(model, train_dl, val_dl=None, epochs=20, lr=1e-3, device="cuda", save_checkpoint=True, manual_seed=69):
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    torch.manual_seed(manual_seed)
    torch.cuda.manual_seed_all(manual_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        total_iou = 0.0
        total_batches = 0
        train_start = time.time()
        avg_batch_time = None

        for i, (imgs, targets) in enumerate(train_dl):
            batch_start = time.time()
            imgs, targets = imgs.to(device), targets.to(device)

            preds = model(imgs)
            bbox_preds, obj_preds = preds[:, :4], preds[:, 4:]
            bbox_targets, obj_targets = targets[:, :4], targets[:, 4:]

            bbox_loss = F.mse_loss(bbox_preds, bbox_targets)
            obj_loss = F.binary_cross_entropy_with_logits(obj_preds, obj_targets)
            loss = bbox_loss + obj_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_iou += compute_iou(bbox_preds, bbox_targets)
            total_batches += 1

            batch_time = time.time() - batch_start
            avg_batch_time = smooth_ema(avg_batch_time, batch_time)
            batches_left = len(train_dl) - (i + 1)
            est_time_left = avg_batch_time * batches_left
            elapsed_time = time.time() - train_start

            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {total_loss / total_batches:.4f} | "
                f"Train IoU: {total_iou / total_batches:.4f} | "
                f"Batch: {i+1}/{len(train_dl)} | "
                f"Elapsed: {format_time(elapsed_time)} | ETA: {format_time(est_time_left)}",
                end='\r'
            )

        print()
        print(f"Epoch [{epoch+1:02d}/{epochs:02d}] | Train Loss: {total_loss / total_batches:.4f} | Train IoU: {total_iou / total_batches:.4f}")

        if val_dl:
            model.eval()
            val_loss = 0.0
            val_iou = 0.0
            val_batches = 0
            val_start = time.time()
            avg_val_batch_time = None

            with torch.inference_mode():
                for i, (imgs, targets) in enumerate(val_dl):
                    batch_start = time.time()
                    imgs, targets = imgs.to(device), targets.to(device)

                    preds = model(imgs)
                    bbox_preds, obj_preds = preds[:, :4], preds[:, 4:]
                    bbox_targets, obj_targets = targets[:, :4], targets[:, 4:]

                    bbox_loss = F.mse_loss(bbox_preds, bbox_targets)
                    obj_loss = F.binary_cross_entropy_with_logits(obj_preds, obj_targets)
                    loss = bbox_loss + obj_loss

                    val_loss += loss.item()
                    val_iou += compute_iou(bbox_preds, bbox_targets)
                    val_batches += 1

                    batch_time = time.time() - batch_start
                    avg_val_batch_time = smooth_ema(avg_val_batch_time, batch_time)
                    est_time_left = avg_val_batch_time * (len(val_dl) - (i + 1))
                    elapsed_time = time.time() - val_start

                    print(
                        f"Epoch [{epoch+1:02d}/{epochs:02d}] | Val Loss: {val_loss / val_batches:.4f} | "
                        f"Val IoU: {val_iou / val_batches:.4f} | "
                        f"Batch: {i+1}/{len(val_dl)} | Elapsed: {format_time(elapsed_time)} | ETA: {format_time(est_time_left)}",
                        end='\r'
                    )

            print()
            print(f"Epoch [{epoch+1:02d}/{epochs:02d}] | Val Loss: {val_loss / val_batches:.4f} | Val IoU: {val_iou / val_batches:.4f}")

        if save_checkpoint:
            torch.save(model.state_dict(), f"DetectionWeights_epoch{epoch+1}.pth")

    return model

def train_recognition(model, train_dl, val_dl=None, epochs=20, lr=1e-3, device="cuda", save_checkpoint=True, manual_seed=69):
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    torch.manual_seed(manual_seed)
    torch.cuda.manual_seed_all(manual_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        train_start = time.time()
        avg_batch_time = None

        for i, (imgs, labels) in enumerate(train_dl):
            batch_start = time.time()
            imgs, labels = imgs.to(device), labels.to(device)

            logits = model(imgs, labels)
            loss = criterion(logits, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * labels.size(0)
            preds = logits.argmax(dim=1)
            total_correct += (preds == labels).sum().item()
            total_samples += labels.size(0)

            batch_time = time.time() - batch_start
            avg_batch_time = smooth_ema(avg_batch_time, batch_time)
            est_time_left = avg_batch_time * (len(train_dl) - (i + 1))
            elapsed_time = time.time() - train_start

            print(
                f"Epoch [{epoch+1:02d}/{epochs:02d}] | "
                f"Train Loss: {total_loss / total_samples:.4f} | "
                f"Train Acc: {100 * total_correct / total_samples:6.2f}% | "
                f"Batch: {i+1}/{len(train_dl)} | "
                f"Elapsed: {format_time(elapsed_time)} | ETA: {format_time(est_time_left)}",
                end='\r'
            )

        print()
        print(f"Epoch [{epoch+1:02d}/{epochs:02d}] | Train Loss: {total_loss / total_samples:.4f} | Train Acc: {100 * total_correct / total_samples:.2f}%")

        if val_dl:
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_samples = 0
            avg_val_batch_time = None
            val_start = time.time()

            with torch.inference_mode():
                for i, (imgs, labels) in enumerate(val_dl):
                    batch_start = time.time()
                    imgs, labels = imgs.to(device), labels.to(device)

                    logits = model(imgs, labels)
                    loss = criterion(logits, labels)

                    val_loss += loss.item() * labels.size(0)
                    preds = logits.argmax(dim=1)
                    val_correct += (preds == labels).sum().item()
                    val_samples += labels.size(0)

                    batch_time = time.time() - batch_start
                    avg_val_batch_time = smooth_ema(avg_val_batch_time, batch_time)
                    est_time_left = avg_val_batch_time * (len(val_dl) - (i + 1))
                    elapsed_time = time.time() - val_start

                    print(
                        f"Epoch [{epoch+1:02d}/{epochs:02d}] | Val Loss: {val_loss / val_samples:.4f} | "
                        f"Val Acc: {100 * val_correct / val_samples:6.2f}% | "
                        f"Batch: {i+1}/{len(val_dl)} | "
                        f"Elapsed: {format_time(elapsed_time)} | ETA: {format_time(est_time_left)}",
                        end='\r'
                    )

            print()
            print(f"Epoch [{epoch+1:02d}/{epochs:02d}] | Val Loss: {val_loss / val_samples:.4f} | Val Acc: {100 * val_correct / val_samples:.2f}%")

        if save_checkpoint:
            torch.save(model.state_dict(), f"RecognitionWeights_epoch{epoch+1}.pth")

    return model
