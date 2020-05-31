from torch.utils.data import DataLoader
import statistics
from dataset import DAVISDataset
import torch
from torchvision.transforms import Compose, ToTensor, Normalize
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
from helpers.utils import convert_mask_pred_to_ground_truth_format, intersection_over_union, revert_normalization


def evaluate(model, device, writer=None, global_step=None):
    overlap = model.fast_pathway_size // 2
    means = [0.485, 0.456, 0.406]
    stds = [0.229, 0.224, 0.225]
    transforms = Compose([ToTensor(), Normalize(mean=means,
                                                std=stds)])
    dataset = DAVISDataset(root='data/DAVIS', subset='val', transforms=transforms, max_seq_length=50,
                           fast_pathway_size=16)
    dataloader = DataLoader(dataset, batch_size=1)
    model.eval()

    intersection_over_unions = []
    total_loss = 0.
    count = 0
    plotted = False

    for seq in tqdm(dataloader, total=len(dataloader), desc="Evaluating with Sequence:"):
        preds = []
        imgs, gt_masks, boxes, padding = seq
        imgs = torch.cat(imgs).to(device)
        count += imgs.shape[0] - (int(padding[0]) * overlap) - (int(padding[1]) * overlap)
        with torch.no_grad():
            loss, output = model(imgs, boxes, gt_masks, padding)
            total_loss += loss.item()
            preds.extend(output)

        # imgs can contain padding values not predicted by the model, delete them
        if not padding[0].item():
            imgs = imgs[overlap:]
            gt_masks = gt_masks[overlap:]
            boxes = boxes[overlap:]
        if not padding[1].item():
            imgs = imgs[:-overlap]
            gt_masks = gt_masks[:-overlap]
            boxes = boxes[:-overlap]

        mask_idx = 0
        plt_needed = False
        for img_idx, (img_boxes, img_gt_masks) in enumerate(zip(boxes, gt_masks)):
            img = imgs[img_idx].cpu().numpy().transpose(1, 2, 0)
            if not plotted:
                ax = plt.subplot(1, 1, 1)
                ax.set_axis_off()
                ax.imshow(revert_normalization(img, means=means, stds=stds))
                plotted_count = 0
                plt_needed = True
            for box, gt_mask in zip(img_boxes, img_gt_masks):  # Wont work when not using gt_boxes because we can have less boxes than masks
                box = box[0].tolist()
                mask = preds[mask_idx].cpu().numpy().astype(np.float)
                mask_idx += 1

                full_mask = convert_mask_pred_to_ground_truth_format(img=img, box=box, mask=mask, threshold=0.5)
                iou = intersection_over_union(gt_mask[0].numpy(), full_mask)
                intersection_over_unions.append(iou)

                if not plotted:
                    full_mask = np.expand_dims(full_mask, axis=-1).repeat(4, axis=-1)
                    full_mask[:, :, 0] = 0.
                    full_mask[:, :, 1] = 1
                    full_mask[:, :, 2] = 0.

                    ax.imshow(full_mask, alpha=0.3)
                    plotted_count += 1
                    if plotted_count == len(img_boxes):
                        plotted = True

            if plt_needed:
                plt.savefig(f'data/output/eval_output/{global_step}_{mask_idx}.png')
                plt_needed = False

    mean_iou = statistics.mean(intersection_over_unions)
    median_iou = statistics.median(intersection_over_unions)
    total_loss = total_loss / count

    print(f'\nVal Loss: {total_loss:.4f}\n'
          f'Mean_IoU: {mean_iou:.4f}\n'
          f'Median_IoU: {median_iou:.4f}\n')

    if writer is not None and global_step is not None:
        writer.add_scalar('Loss/Val', total_loss, global_step=global_step)
        writer.add_scalar('IoU/Mean', mean_iou, global_step=global_step)
        writer.add_scalar('IoU/Median', median_iou, global_step=global_step)

    return mean_iou, total_loss
