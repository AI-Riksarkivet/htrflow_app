default_scope = "mmdet"
default_hooks = dict(
    timer=dict(type="IterTimerHook"),
    logger=dict(type="LoggerHook", interval=100),
    param_scheduler=dict(type="ParamSchedulerHook"),
    checkpoint=dict(type="CheckpointHook", interval=1, max_keep_ckpts=5, save_best="auto"),
    sampler_seed=dict(type="DistSamplerSeedHook"),
    visualization=dict(type="DetVisualizationHook"),
)
env_cfg = dict(cudnn_benchmark=False, mp_cfg=dict(mp_start_method="fork", opencv_num_threads=0), dist_cfg=dict(backend="nccl"))
vis_backends = [dict(type="LocalVisBackend")]
visualizer = dict(type="DetLocalVisualizer", vis_backends=[dict(type="LocalVisBackend")], name="visualizer", save_dir="./")
log_processor = dict(type="LogProcessor", window_size=50, by_epoch=True)
log_level = "INFO"
load_from = "/home/erik/Riksarkivet/Projects/HTR_Pipeline/models/checkpoints/rtmdet_regions_6/epoch_11.pth"
resume = True
train_cfg = dict(type="EpochBasedTrainLoop", max_epochs=12, val_interval=12, dynamic_intervals=[(10, 1)])
val_cfg = dict(type="ValLoop")
test_cfg = dict(
    type="TestLoop",
    pipeline=[
        dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
        dict(type="Resize", scale=(640, 640), keep_ratio=True),
        dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
        dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
    ],
)
param_scheduler = [
    dict(type="LinearLR", start_factor=1e-05, by_epoch=False, begin=0, end=1000),
    dict(type="CosineAnnealingLR", eta_min=1.25e-05, begin=6, end=12, T_max=6, by_epoch=True, convert_to_iter_based=True),
]
optim_wrapper = dict(
    type="OptimWrapper",
    optimizer=dict(type="AdamW", lr=0.00025, weight_decay=0.05),
    paramwise_cfg=dict(norm_decay_mult=0, bias_decay_mult=0, bypass_duplicate=True),
)
auto_scale_lr = dict(enable=False, base_batch_size=16)
dataset_type = "CocoDataset"
data_root = "data/coco/"
file_client_args = dict(backend="disk")
train_pipeline = [
    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
    dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
    dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
    dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
    dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
    dict(type="YOLOXHSVRandomAug"),
    dict(type="RandomFlip", prob=0.5),
    dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
    dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
    dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
    dict(type="PackDetInputs"),
]
test_pipeline = [
    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
    dict(type="Resize", scale=(640, 640), keep_ratio=True),
    dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
    dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
]
tta_model = dict(type="DetTTAModel", tta_cfg=dict(nms=dict(type="nms", iou_threshold=0.6), max_per_img=100))
img_scales = [(640, 640), (320, 320), (960, 960)]
tta_pipeline = [
    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
    dict(
        type="TestTimeAug",
        transforms=[
            [
                {"type": "Resize", "scale": (640, 640), "keep_ratio": True},
                {"type": "Resize", "scale": (320, 320), "keep_ratio": True},
                {"type": "Resize", "scale": (960, 960), "keep_ratio": True},
            ],
            [{"type": "RandomFlip", "prob": 1.0}, {"type": "RandomFlip", "prob": 0.0}],
            [{"type": "Pad", "size": (960, 960), "pad_val": {"img": (114, 114, 114)}}],
            [
                {
                    "type": "PackDetInputs",
                    "meta_keys": ("img_id", "img_path", "ori_shape", "img_shape", "scale_factor", "flip", "flip_direction"),
                }
            ],
        ],
    ),
]
model = dict(
    type="RTMDet",
    data_preprocessor=dict(
        type="DetDataPreprocessor", mean=[103.53, 116.28, 123.675], std=[57.375, 57.12, 58.395], bgr_to_rgb=False, batch_augments=None
    ),
    backbone=dict(
        type="CSPNeXt",
        arch="P5",
        expand_ratio=0.5,
        deepen_factor=0.67,
        widen_factor=0.75,
        channel_attention=True,
        norm_cfg=dict(type="SyncBN"),
        act_cfg=dict(type="SiLU", inplace=True),
    ),
    neck=dict(
        type="CSPNeXtPAFPN",
        in_channels=[192, 384, 768],
        out_channels=192,
        num_csp_blocks=2,
        expand_ratio=0.5,
        norm_cfg=dict(type="SyncBN"),
        act_cfg=dict(type="SiLU", inplace=True),
    ),
    bbox_head=dict(
        type="RTMDetInsSepBNHead",
        num_classes=80,
        in_channels=192,
        stacked_convs=2,
        share_conv=True,
        pred_kernel_size=1,
        feat_channels=192,
        act_cfg=dict(type="SiLU", inplace=True),
        norm_cfg=dict(type="SyncBN", requires_grad=True),
        anchor_generator=dict(type="MlvlPointGenerator", offset=0, strides=[8, 16, 32]),
        bbox_coder=dict(type="DistancePointBBoxCoder"),
        loss_cls=dict(type="QualityFocalLoss", use_sigmoid=True, beta=2.0, loss_weight=1.0),
        loss_bbox=dict(type="GIoULoss", loss_weight=2.0),
        loss_mask=dict(type="DiceLoss", loss_weight=2.0, eps=5e-06, reduction="mean"),
    ),
    train_cfg=dict(assigner=dict(type="DynamicSoftLabelAssigner", topk=13), allowed_border=-1, pos_weight=-1, debug=False),
    test_cfg=dict(nms_pre=200, min_bbox_size=0, score_thr=0.4, nms=dict(type="nms", iou_threshold=0.6), max_per_img=50, mask_thr_binary=0.5),
)
train_pipeline_stage2 = [
    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
    dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
    dict(type="RandomResize", scale=(640, 640), ratio_range=(0.1, 2.0), keep_ratio=True),
    dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
    dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
    dict(type="YOLOXHSVRandomAug"),
    dict(type="RandomFlip", prob=0.5),
    dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
    dict(type="PackDetInputs"),
]
train_dataloader = dict(
    batch_size=2,
    num_workers=1,
    batch_sampler=None,
    pin_memory=True,
    persistent_workers=True,
    sampler=dict(type="DefaultSampler", shuffle=True),
    dataset=dict(
        type="ConcatDataset",
        datasets=[
            dict(
                type="CocoDataset",
                metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
                data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/"),
                ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/gt_files/coco_regions2.json",
                pipeline=[
                    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
                    dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
                    dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
                    dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
                    dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
                    dict(type="YOLOXHSVRandomAug"),
                    dict(type="RandomFlip", prob=0.5),
                    dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
                    dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
                    dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
                    dict(type="PackDetInputs"),
                ],
            ),
            dict(
                type="CocoDataset",
                metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
                data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
                ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
                pipeline=[
                    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
                    dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
                    dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
                    dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
                    dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
                    dict(type="YOLOXHSVRandomAug"),
                    dict(type="RandomFlip", prob=0.5),
                    dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
                    dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
                    dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
                    dict(type="PackDetInputs"),
                ],
            ),
        ],
    ),
)
val_dataloader = dict(
    batch_size=1,
    num_workers=10,
    dataset=dict(
        pipeline=[
            dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
            dict(type="Resize", scale=(640, 640), keep_ratio=True),
            dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
            dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
        ],
        type="CocoDataset",
        metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
        data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
        ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/gt_files/coco_regions2.json",
        test_mode=True,
    ),
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type="DefaultSampler", shuffle=False),
)
test_dataloader = dict(
    batch_size=1,
    num_workers=10,
    dataset=dict(
        pipeline=[
            dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
            dict(type="Resize", scale=(640, 640), keep_ratio=True),
            dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
            dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
        ],
        type="CocoDataset",
        metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
        data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
        ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/gt_files/coco_regions2.json",
        test_mode=True,
    ),
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type="DefaultSampler", shuffle=False),
)
max_epochs = 12
stage2_num_epochs = 2
base_lr = 0.00025
interval = 12
val_evaluator = dict(
    proposal_nums=(100, 1, 10),
    metric=["bbox", "segm"],
    type="CocoMetric",
    ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
)
test_evaluator = dict(
    proposal_nums=(100, 1, 10),
    metric=["bbox", "segm"],
    type="CocoMetric",
    ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
)
custom_hooks = [
    dict(type="EMAHook", ema_type="ExpMomentumEMA", momentum=0.0002, update_buffers=True, priority=49),
    dict(
        type="PipelineSwitchHook",
        switch_epoch=10,
        switch_pipeline=[
            dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
            dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
            dict(type="RandomResize", scale=(640, 640), ratio_range=(0.1, 2.0), keep_ratio=True),
            dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
            dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
            dict(type="YOLOXHSVRandomAug"),
            dict(type="RandomFlip", prob=0.5),
            dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
            dict(type="PackDetInputs"),
        ],
    ),
]
work_dir = "/home/erik/Riksarkivet/Projects/HTR_Pipeline/models/checkpoints/rtmdet_regions_6"
train_batch_size_per_gpu = 2
val_batch_size_per_gpu = 1
train_num_workers = 1
num_classes = 1
metainfo = dict(classes="TextRegion", palette=[(220, 20, 60)])
icdar_2019 = dict(
    type="CocoDataset",
    metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
    data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
    ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
    pipeline=[
        dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
        dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
        dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
        dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
        dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
        dict(type="YOLOXHSVRandomAug"),
        dict(type="RandomFlip", prob=0.5),
        dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
        dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
        dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
        dict(type="PackDetInputs"),
    ],
)
icdar_2019_test = dict(
    type="CocoDataset",
    metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
    data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
    ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
    test_mode=True,
    pipeline=[
        dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
        dict(type="Resize", scale=(640, 640), keep_ratio=True),
        dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
        dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
    ],
)
police_records = dict(
    type="CocoDataset",
    metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
    data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/"),
    ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/gt_files/coco_regions2.json",
    pipeline=[
        dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
        dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
        dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
        dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
        dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
        dict(type="YOLOXHSVRandomAug"),
        dict(type="RandomFlip", prob=0.5),
        dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
        dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
        dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
        dict(type="PackDetInputs"),
    ],
)
train_list = [
    dict(
        type="CocoDataset",
        metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
        data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/"),
        ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/police_records/gt_files/coco_regions2.json",
        pipeline=[
            dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
            dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
            dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
            dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
            dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
            dict(type="YOLOXHSVRandomAug"),
            dict(type="RandomFlip", prob=0.5),
            dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
            dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
            dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
            dict(type="PackDetInputs"),
        ],
    ),
    dict(
        type="CocoDataset",
        metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
        data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
        ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
        pipeline=[
            dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
            dict(type="LoadAnnotations", with_bbox=True, with_mask=True, poly2mask=False),
            dict(type="CachedMosaic", img_scale=(640, 640), pad_val=114.0),
            dict(type="RandomResize", scale=(1280, 1280), ratio_range=(0.1, 2.0), keep_ratio=True),
            dict(type="RandomCrop", crop_size=(640, 640), recompute_bbox=True, allow_negative_crop=True),
            dict(type="YOLOXHSVRandomAug"),
            dict(type="RandomFlip", prob=0.5),
            dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
            dict(type="CachedMixUp", img_scale=(640, 640), ratio_range=(1.0, 1.0), max_cached_images=20, pad_val=(114, 114, 114)),
            dict(type="FilterAnnotations", min_gt_bbox_wh=(1, 1)),
            dict(type="PackDetInputs"),
        ],
    ),
]
test_list = [
    dict(
        type="CocoDataset",
        metainfo=dict(classes="TextRegion", palette=[(220, 20, 60)]),
        data_prefix=dict(img="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/"),
        ann_file="/media/erik/Elements/Riksarkivet/data/datasets/htr/segmentation/ICDAR-2019/clean/gt_files/coco_regions2.json",
        test_mode=True,
        pipeline=[
            dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
            dict(type="Resize", scale=(640, 640), keep_ratio=True),
            dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
            dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
        ],
    )
]
pipeline = [
    dict(type="LoadImageFromFile", file_client_args=dict(backend="disk")),
    dict(type="Resize", scale=(640, 640), keep_ratio=True),
    dict(type="Pad", size=(640, 640), pad_val=dict(img=(114, 114, 114))),
    dict(type="PackDetInputs", meta_keys=("img_id", "img_path", "ori_shape", "img_shape", "scale_factor")),
]
launcher = "pytorch"
