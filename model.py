from torch.hub import load as hub_load

model = hub_load('ultralytics/yolov5:master', 'yolov5s', pretrained=True)
model.eval()
 