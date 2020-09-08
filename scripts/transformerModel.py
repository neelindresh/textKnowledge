from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch
model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
label_list = ["O",       # Outside of a named entity
     "B-MISC",  # Beginning of a miscellaneous entity right after another miscellaneous entity
     "I-MISC",  # Miscellaneous entity
     "B-PER",   # Beginning of a person's name right after another person's name
     "I-PER",   # Person's name
     "B-ORG",   # Beginning of an organisation right after another organisation
     "I-ORG",   # Organisation
     "B-LOC",   # Beginning of a location right after another location
    "I-LOC"   ] # Location ]
sequences = '''
In previous chapter, we discussed how different methodologies attempted to classify each pixel in an image. In this article, we will elaborate how instance segmentation classifies each pixel and identifies unique occurrences within a category.In summer 2014, based on R-CNN, Simultaneous Detection and Segmentation (SDS) was conceived. As seen on the image below, it consists of 4 phases.For Proposal Generation, Multiscale Combinatorial Grouping (MCG) was used to generate 2000 region candidates per image.From the input image a multiresolution image pyramid was created. Afterwards, hierarchical segmentation for each scale is performed. By aligning these multiple hierarchies and combining them into a single multiscale segmentation hierarchy, we can group those components and produce a list of object proposals.For each region, a CNN is used for Feature Extraction. For both cropped boxes and region foregrounds individual CNN's were trained, consisting of 5 convolutions followed by 2 fully connected layers. Those features are then fed into a linear SVM, i.e. Region Classification, to assign a score for each category to each candidate. Regions with a score above a threshold are finally fed into the Region Refinement module.For each region, we first learn to predict a coarse, top-down figure-ground mask which is then discretized. Using the features from the CNN and the discretized figure-ground mask, a logistic regression classifier is trained to predict the probability that a cell belongs to the foreground. This results in a prediction about the shape of the object but does not necessarily respect the bottom-up contours. As such, a second classifier is trained to combine this coarse mask with the region candidate. For each pixel we then predict if it belongs to the original region candidate.September 2015, Facebook AI Research (FAIR) team proposed the first algorithm to learn to generate segmentation proposals directly from raw image data, DeepMask. Based on a Convolutional Networks, for a given input image, it will generate a class-agnostic mask and associated score estimating the likelihood of a patch containing a centered object.Using transfer learning on a pretrained VGG for classification on ImageNet, the architecture above was retrained on MS COCO. As such, a large part of the network is shared for the aforementioned tasks. Removing the fully connected layer, we then create a brand for each task. The top branch represents the segmentation head whereas the bottom branch is the objectness branch.The segmentation head is constructed of a 1x1 convolution followed by a classification layer consisting of h x w pixel classifier. Each classifier is responsible to assign whether the corresponding pixel belongs to the object. To achieve this, each pixelwise classifier must utilize the entire feature map so that the network will output a mask for each single object present in an image.The objectness head predicts if an image patch satisfies the following:The output is a score indicating the presence of an object satisfying the previously mentioned constraints.The FAIR team introduces in 2016 an improvement over DeepMask. Then, the encoder-decoder architecture proved to be a feasible solution to generate pixelwise fine-grained segmentations. Similar to what was discussed in previous story, by combining information from the low-level features which comes from early layers with high-level object information coming from deeper layers in the network, the coarseness issue is addressed.Utilising an improved DeepMask architecture for the forward pass, a coarse mask encoding is generated, representing a feature map with multiple channels. This is then progressively integrated with information from previous layers by the use of refinement modules. Each refinement module doubles the spatial resolution by combining the feature map from the forward pass with the mask generated from the previous refinement module until full resolution is achieved and a final output encodes the object mask.Departing from Fast-RCNN, FAIR addresses the following detection challenges :Once more departing from DeepMask, MultiPathNet introduces 3 major modifications:Each input image is fed into the VGG where ROI pooling is used to extract features from the region proposals. For each object proposal, 4 different region crops are created and centered on the object proposal for the purpose of viewing the object at multiple scales, so-called foveal regions. Each region crop is passed through a fully connected layers, concatenated and passed to a classification and regression head.If you recall, Fast R-CNN performs RoI-pooling after the 5th layer in VGG. As such, features have been downsampled by a factor of 16 and thus most spatial information will have been lost for smaller objects. Effective localisation of small objects requires higher-resolution features from earlier layers and thus we take the features from the 3rd to 5th convolution layers and provide them to each foveal classifier.Typically, during training a fixed IoU threshold is chosen. In this case, an integral loss function was introduced to encourage the model to perform well at multiple IoU thresholds.We will start with arguably the most popular architecture created by the Facebook AI Research team. As we will see, Faster R-CNN constitutes the fundamental block on which Mask R-CNN is built upon. As such, let us refresh some concepts.Recall that Faster R-CNN generates 2 outputs: class labels and boundary boxes. After extracting features, a region proposal network (RPN) is employed to generate region of interests (RoI). These RoI are then resized and passed to a set of fully convolutional (FC) layers.At its essence, Mask R-CNN extends Faster R-CNN with a 3rd branch which generates the output masks. By overlaying on each bounding box a mask and taking into account the class label, we would obtain a semantic segmentation result. Additionally, each bounding box delineates a specific instance of an object resulting in segmentation masks which denotes the various instances of a class.The training is formulated as a multi task loss which is the sum of the classification loss, bounding-box loss and mask loss.A nuanced but big contribution of Mask RCNN is the introduction of ROI Align. If normal pooling were to be used we would basically introduce rounding errors twice in the pipeline, as seen below.The first error occurs when coordinates from the original input image are mapped to the coordinates on the feature map. The second error, is at the pooling phase itself where those rounded off coordinates get quantized and results into a loss of information.ROI Align solves this issue with the following steps:This modification can result in an increase of up to 10% making Mask RCNN a reference in the instance segmentation literature and a widely used architecture for a broad set of applications.In 2018, researchers propose PANet by improving the propagation in Mask RCNN. The 3 contributions are:Features are extracted using a FPN backbone. Based on the fact that neurons in the higher layers respond to objects whereas neurons in the lower level responds more likely to local patterns and structures and that low-level patterns and structures are a high indicator of instances. We can conclude that increased instance localisation can occur if propagating strong responses of low-level patterns. This propagation, illustrated above with the dashed green line, is created by introducing a shortcut of less than 10 layers instead of the 100+ layers.The bottom-up path augmentation happens on the output of the FPN which results in feature maps (Ni) having the same spatial size as the corresponding FPN output stage (Pi).To reduce the spatial size, feature map Ni first goes through a 3×3 conv layer with stride 2 and ReLU.Finally, featuremap Ni+1 is created by fusing both maps and passing it through another 3x3 conv layer and ReLU.Each proposal is then mapped to different feature levels and fed into Mask R-CNN's ROIAlign layer where feature grids from each level is pooled. The feature grids are then fused using a sum or elementwise-max.The motivation follows the one stated earlier. High-level features have a large receptive field and capture richer context information, combining them with small proposals can be beneficial due to the fact that low-level features contain many fine details and high localisation accuracy.Similar to Mask R-CNN, the output of the pooling feeds 3 branches to compute the class, box and masks. A fully connected layer takes care of class classification and box regression. Below, we observe the pipeline for the mask component.Each conv layer consists of 256 3×3 filters and the deconvolutional layer up-samples feature with factor 2. Again similar to Mask R-CNN, segmentation and classification are decoupled by predicting a binary pixel-wise mask for each class independently. From conv3 a small branch is created where a fully connected layer predicts a class-agnostic foreground/background mask. Doing this, increases the generality and reduces the loss in spatial information.Fall 2019, the first YOLO-based model was created by breaking instance segmentation into two parallel tasks: generating a set of prototype masks and predicting per-instance mask coefficient. Combining those prototype masks with the mask coefficient results in instance masks. Typical instance segmentation approaches will first generate candidate region of interests followed by classification and segmentation. YOLACT differs in this matter by adding a mask branch to an existing one-stage object detection model without any feature localization steps.Based on a RetinaNet backbone, two branches are created. Firstly, Protonet, which is a FCN, generates image-sized prototype masks independent of instance. Secondly, the Prediction Head predicts a vector of mask coefficients corresponding to each prototype.Pixels of the same instance have a higher likelihood of being from the same instance. Convolutional layers do take this into account whereas a fully connected layer doesn’t. As such, we split the branches where fully-connected layers do produce excellent semantic vectors and let the convolution layers create spatially coherent masks.Protonet is a simple sequence of 3x3 convolutions except for the final convolution which is 1x1. The deepest layer of FPN is used to produce higher resolution prototypes resulting in both higher quality masks and better performance on smaller objects.Anchor-based object detectors have two branches in their prediction heads: one to calculate class confidence and one to calculate the bounding box regressor. Turns out by simply adding a branch, mask coefficients for each prototype can be calculated."YOLACT learns how to localize instances on its own via different activations in its prototypes."One would then assume that increasing the amount of prototypes would increase the performance. Predicting the mask coefficients is not easy and thus, if coefficients are too erroneous due the linear combination of prototype masks and coefficients the resulting instance mask can completely vanish or include other objects. As such, a balancing act is required to obtain the right amount of prototypes and corresponding coefficients.Introduces some cool upgrades to YOLACT:Using a ResNet as backbone, each 3x3 convolutional layer was replaced by a deformable convolution layer which improves the handling of instances with different scales, aspect ratios and rotations.As we know by now, standard convolution operates on a grid of an input with a predefined size. To accommodate geometric variations we can either build a dataset with sufficient variations or employ transformation-invariant features and algorithms. As we see below, by adding a learnable offset to a regular grid a freedom exist to generalize across various transformations, aspect ratios and rotations.Prediction heads were optimized by simply tuning the hyper-parameters of the anchor-based backbone. Variations were made by "keeping the scales unchanged while increasing the anchor aspect ratios and keeping the aspect ratios unchanged while increasing the scales per FPN level by threefold."It was observed that mask segmentations with high quality don’t necessarily have higher class confidences. By learning to regress the predicted mask to its mask IoU with ground-truth, the network learns to better correlate class confidence with mask quality. As seen, it consists of 6 convolutional layers (followed by ReLU) and 1 global pooling layer.It is clear to understand the challenges present in the task of instance segmentation. The recurring question which all architectures are trying to answer is related to how to the global visual context of the image take into account to improve the prediction of the segmentation. Instance segmentation being the crème de la crème, as compared to image classification, object detection and semantic segmentation, is a hot topic. Fine in granularity it also provides a first glance in obtaining contextual information. Many architectures are focused in improving performances regardless (more or less) of computational intensity, it can be expected to see an increase in architectures developed toward real-timeness and mobile applications.Written byWritten by
'''
final_toks=[]
for sequence in sequences.split("."):
    print(sequence)
# Bit of a hack to get the tokens with the special tokens
    tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(sequence)))
    inputs = tokenizer.encode(sequence, return_tensors="pt")
    outputs = model(inputs)[0]
    predictions = torch.argmax(outputs, dim=2)

    alltokens=[(token, label_list[prediction]) for token, prediction in zip(tokens, predictions[0].numpy()) if label_list[prediction]!="O"]
    prev=""
    all_toks=[]
    for i in alltokens:
        data=i[0]
        if i[0].startswith("##"):
            data=prev+data[2:]
            prev = data
            continue
        
        if prev != "" and prev not in all_toks:all_toks.append(prev)
        if data in sequence.split() and data not in all_toks:
            all_toks.append(data)
        prev=data
    if len(alltokens)>0 and alltokens[-1][0]!= prev:
        all_toks.append(prev)
    final_toks.extend(all_toks)
    
    