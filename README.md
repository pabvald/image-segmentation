# Neural Networks: Implementation and Application - Computer Vision Project 

Authors: Tomás Amado Peters (@tomasamado), Pablo Valdunciel Sanchez (@pabvald)

### Abstract
Image segmentation has important applications in different fields such as medical imaging (diagnosis, surgery planning,...), recognition tasks (face recognition) and computer vision. Segmentation methods based on deep neural networks have been evolving and achieving higher performance in different tasks over the last years. In this report, we summarize our work within the Computer Vision project of the *Neural Networks: Theory and Implementation* (WiSem2020/21) course at Saarland University, which focuses on understanding and implementing different neural network models for the mentioned methods. During this project, we familiarised ourselves with two image segmentation datasets: the well known PASCAL Visual Object Classes (PASCAL VOC) and the Cityscapes datasets. We successfully implemented a version of the R2U-Net model used in medical image segmentation, named R2U-Net64, that can be used in multi-class pixel-level segmentation tasks with the Cityscapes dataset and we improved this model's performance by implementing and including a module based on height-driven attention networks (HANet) into the architecture.

![Screenshot 2024-09-04 at 10 29 11](https://github.com/user-attachments/assets/b6e96c58-6258-41db-b854-079acc5a6ba6)

### Report 

We have elaborated a [report](./docs/report.pdf) in the NIPS 2020 format explaining in detail our work during this project.

### Notebooks 

- [Task 1: SimpleSegNet, PascalVOC dataset](https://nbviewer.jupyter.org/github/pabvald/image-segmentation/blob/main/Vision_task_1.ipynb)
- [Task 2: R2-Unet, Cityscapes dataset](https://nbviewer.jupyter.org/github/pabvald/image-segmentation/blob/main/Vision_task_2.ipynb)
- [Task 3: R2-Unet + HANet, Cityscapes dataset](https://nbviewer.jupyter.org/github/pabvald/image-segmentation/blob/main/Vision_task_3.ipynb)
