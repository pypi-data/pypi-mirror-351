# -*- coding: utf-8 -*-

__version__   = '2.5.5'
__author__    = "Avinash Kak (kak@purdue.edu)"
__date__      = '2025-May-28'                   
__url__       = 'https://engineering.purdue.edu/kak/distDLS/DLStudio-2.5.5.html'
__copyright__ = "(C) 2025 Avinash Kak. Python Software Foundation."


__doc__ = '''

DLStudio.py

Version: ''' + __version__ + '''
   
Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''


@tag_changes
CHANGE LOG:

  Version 2.5.5:

    With the inclusion of VQGAN, this version of DLStudio incorporates all three
    foundational concepts in variational autoencoding: VAE, VQVAE and VQGAN .  The
    last, VQGAN, occupies a very special place in Deep Learning because it
    established unequivocally that, after tokenization, attention based processing
    with transformers can be made to work exactly the same for both languages and
    images.  This is in keeping with the belief held by researchers (psychologists,
    psychophysicists, cognitive scientists, etc.) that after the lowest levels of
    sensory processing, the brain uses the same structures for drawing high level
    inferences from different types of sensory signals. And the fact that many people
    tend to be highly imagistic readers lends further support to this idea of the
    presence of unified structures in the brain for high-level processing of sensory
    information regardless of the sensors involved.

  Version 2.5.4:

    I have significantly redesigned the neural networks for the autoencoding classes
    in DLStudio.  These classes are Autoencoder, VAE, and VQVAE. These networks can
    now be made arbitrarily deep with a single parameter named num_repeats that
    controls the number of repetitions of the SkipBlock instances for which the
    channel dimensionality remains unchanged from the input to the output.

  Version 2.5.3:

    I have fixed the v2.5.2 module packaging error in the new version.  In addition,
    I have also changed the tensor axis used for nn.Softmax normalization of the
    "Q.K^T" dot-products from the word axis in the Q-tensors to the word-axis in the
    K-tensors.  This could potentially lead to superior results when solving problems
    in which the cross-attention plays a significantly larger role than
    self-attention.

  Version 2.5.2:

    In this version, I have simplified the code in the AdversarialLearning module of
    DLStudio.  This I did by dropping what turned out to be a not-really-needed
    container class for the rest of the code in the module.  Another change made in
    this version is the addition of VQ-VAE code in the main DLStudio class file.
    This added code is in the form of a new class called VQVAE. (BTW, VQ stands for
    Vector Quantization.  It is an important concept that is at the heart of what's
    known as Codebook Learning for more efficient discrete representation of images
    using a finite vocabulary of embedding vectors.) 

  Version 2.5.1:

    With this version, DLStudio now comes with an implementation for Variational
    Auto-Encoding (VAE) for images.  The VAE Encoder learns the latent distribution
    (as represented by the mean and the variance of a presumed isotropic Gaussian)
    for a training dataset.  Subsequently, the VAE Decoder samples this distribution
    for generating new images that can be useful variants of the input images.  My
    VAE implementation is in the form of two additional inner classes in the main
    DLStudio class: Autoencoder and VAE.  The former serves as the base class for the
    latter.

  Version 2.5.0:

    An encoder/decoder component of a typical Transformer consists of an attention
    layer followed by an FFN (Feed Forward Network) layer.  There was an error in the
    FFN layer that I have fixed in this version of DLStudio.  While the previous
    versions also worked from the standpoint of overall transformer-based learning,
    the error caused the number of learnable parameters to depend strongly on the
    maximum sequence length at the input to the transformer.  You will not see that
    problem in Version 2.5.0.  

  Version 2.4.9:

    This version contains fixes for the pathname errors in the Transformers module of
    DLStudio. The errors were related to where the models and the checkpoints were
    supposed to be stored during training.

  Version 2.4.8:

    In this version, I have made two important changes to the Transformers module in
    DLStudio: (1) The Transformers module now includes a new class that I have named
    visTransformer that works like the famous Vision Transformer (ViT) proposed by
    Dosovitskiy et al. And (2) I have made changes to the QKV code for the
    calculation of self and cross attention in all of the Transformer classes in the
    module. The attention calculations should now execute faster, which is a very
    important consideration in any transformer based learning.

  Version 2.4.3:

    The diffusion modeling part of the code should now accept training images of any
    size.  Previously it was limited to images of size 64x64.  Note that this change
    is not as significant as you might think because, under the hood, the actual
    input image size is changed to the size 64x64 for diffusion modeling.  So this
    change is more for your convenience than anything else.  I have also improved the
    image visualization code in the ExamplesDiffusion directory. The new
    implementation of the script VisualizeSamples.py automatically generates a
    collage of the images generated from noise by the script
    GenerateNewImageSamples.py.  Other changes include minor clean-up of the main doc
    page for GenerativeDiffusion module and of a couple of the functions in the
    module.

  Version 2.4.2:

    DLStudio now includes a new module devoted to data modeling with diffusion.  This
    module, named GenerativeDiffusion, is a module in the overall DLStudio platform.
    The GenerativeDiffusion class resides at the same level of software abstraction
    as the main DLStudio class in the platform.  See the README in the
    ExamplesDiffusion directory of the distribution for how to experiment with the
    diffusion based code in DLStudio.

  Version 2.3.6:

    Gets rid of the inadvertently hardcoded value for the batch size in the testing
    part of the code for Semantic Segmentation.

  Version 2.3.5:

    In this version I have improved the quality of the code in the Semantic
    Segmentation inner class of DLStudio.

  Version 2.3.4:

    Contains a cleaner design for the SkipBlock network. That led to improved design
    for some of the larger networks in DLStudio that use the SkipBlock as a
    building-block.

  Version 2.3.3:

    This version fixes a couple of bugs in DLStudio.  The newer versions of PyTorch
    do not like it if, during the forward flow of data through a network, you make
    in-place changes to the data objects that are in the computational graph.
    Examples of in-place operations are those that result from using compound
    assignment operators like '+=', '*=', etc., and those that result from the use of
    slice operators on arrays.  Such bugs are difficult to troubleshoot because the
    error messages returned by PyTorch are as unhelpful as they can be --- they give
    you no indication at all as to the location of the fault. This version of
    DLStudio was tested with Version 2.0.1 of PyTorch.

  Version 2.3.2:

    This version of DLStudio includes a new Metric Learning module (name of the
    class: MetricLearning). The main idea of metric learning is to learn a mapping
    from the images to their embedding vector representations in such a way that the
    embeddings for what are supposed to be similar images are pulled together and
    those for dissimilar images are pulled as far apart as possible.  After such a
    mapping function is learned, you can take a query image (whose class label is not
    known), run it through the network to find its embedding vector, and,
    subsequently, assign to the query image the class label of the nearest
    training-image neighbor in the embedding space.  As explained in my Metric
    Learning lecture slides in the Deep Learning class at Purdue, this approach to
    classification is likely to work better under data conditions when the more
    traditional neural network classifiers fail.

  Version 2.3.0:

    I have made it a bit simpler for you to use DLStudio's transformer classes in
    your own scripts.  This I did by eliminating 'Transformers' as the parent class
    of TransformerFG and TransformerPreLN.  Now, in your own scripts, you can have
    more direct access to these two classes that you need for transformer based
    learning.  Your best guide to the syntax for calling TransformerFG and
    TransformerPreLN are the example scripts "seq2seq_with_transformerFG.py" and
    "seq2seq_with_transformerPreLN.py" in the ExamplesTransformers directory of the
    distribution.  Additional changes in Version 2.3.0 include general code clean-up
    by getting rid of variables no longer being used, harmonizing the names of the
    constructor options, etc.

  Version 2.2.8:

    In this version I have fixed a couple of errors that had crept into the previous
    version at the time of packaging that distribution.

  Version 2.2.7:

    This version provides you with the tools you need to cope with the frustrations
    of training a transformer based network. Such networks in general are difficult
    to train, in the sense that your per-epoch training time is likely to be much
    longer than what you are accustomed to, and it can take many, many more epochs to
    get the model to converge.  In addition, you have the problem of stability to
    deal with. Stability means that with a wrong choice for the hyperparameters, the
    model that you are currently training could suddenly begin to diverge (which is
    something akin to mode collapse in training a GAN). If you have to wait until the
    end of training to see such failures, that can be very frustrating.  To cope with
    these problems, this version of DLStudio automatically spits out a checkpoint for
    the model every 5 epochs and also gives you the functions for evaluating the
    performance of the checkpoints. The performance check can be as simple as looking
    at the translated sentences vis-a-vis their targets for a random selection of
    sentence pairs from the data.  When real learning is taking place, you will see
    longer and longer fragments of the translated sentences correspond to the target
    sentences. On the other hand, when you have model divergence, the translated
    sentences will appear to be gibberish.  A future version of DLStudio will also
    print out the BLEU score for the checkpoints.

  Version 2.2.5:

    This version contains significantly improved documentation for DCGAN and WGAN in
    the AdversarialLearning class of DLStudio.

  Version 2.2.4:

    I have cleaned up the code in the new DIoULoss class that I added in the previous
    version. The script object_detection_and_localization_iou.py in the Examples
    directory of DLStudio is based on this loss function.

  Version 2.2.3:

    The inner class DetectAndLocalize of DLStudio now contains a custom loss function
    provided by the class DIoULoss that implements the more modern variants of the
    basic IoU (Intersection over Union) loss function.  These IoU variants are
    explained in the slides 37-42 of my Week 7 Lecture on "Object Detection and
    Localization."  Your best entry point to become familiar with these loss
    functions is the script object_detection_and_localization_iou.py in the Examples
    directory of DLStudio.

  Version 2.2.2:

    This version of DLStudio presents my implementation of transformers in deep
    learning. You will find two transformer implementations in the Transformers
    module of the DLStudio platform in the distribution directory: TransformerFG and
    TransformerPreLN.  "FG" in TransformerFG stands for "Transformer First
    Generation"; it is my implementation of the architecture presented originally in
    the seminal paper "Attention is All You Need" by Vaswani et el.  And the second,
    TransformerPreLN ("PreLN" stands for "Pre Layer Norm") is a small but important
    modification of the original idea that is based on the paper "On Layer
    Normalization in the Transformer Architecture" by Xiong et al.  I could have
    easily combined the two implementations with a small number of conditional
    statements to account for the differences, however I have chosen to keep them
    separate in order to make it easier for the two to evolve separately and to be
    used differently for educational purposes.

  Versions 2.1.7 through 2.2.1:

    These version numbers are for the stepping-stones in my journey into the world of
    transformers --- my experiments with how to best implement the different
    components of a transformer for educational purposes.  As things stand, these
    versions contain features that did not make into the public release version 2.2.2
    on account of inadequate testing.  I may include those features in versions of
    DLStudio after 2.2.2.

  Version 2.1.6:

    All the changes are confined to the DataPrediction module in the DLStudio
    platform.  After posting the previous version, I noticed that the quality of the
    code in DataPrediction was not up to par.  The new version presents a cleaned-up
    version of the DataPrediction class.

  Version 2.1.5:

    DLStudio has now been equipped with a new module named DataPrediction whose focus
    is solely on solving data prediction problems for time-series data.  A
    time-series consists of a sequence of observations recorded at regular intervals.
    These could, for example, be the price of a stock share recorded every hour; the
    hourly recordings of electrical load at your local power utility company; the
    mean average temperature recorded on an annual basis; and so on.  We want to use
    the past observations to predict the value of the next one.  While data
    prediction has much in common with other forms of sequence based learning, it
    presents certain unique challenges of its own and those are with respect to (1)
    Data Normalization; (2) Input Data Chunking; and (3) Multi-dimensional encoding
    of the "datetime" associated with each observation in the time-series.

  Version 2.1.3:

    Some users of DLStudio have reported that when they run the WGAN code for
    adversarial learning, the dataloader sometimes hangs in the middle of a training
    run.  (A WGAN training session may involve as many as 500 epochs.)  In trying to
    reproduce this issue, I discovered that the training loops always ran to
    completion if you set the number of workers in the dataloader to 0.  Version
    2.1.3 makes it easier for you to specify the number of workers in your own
    scripts that call on the WGAN functionality in the AdversarialLearning class.

  Version 2.1.2:

    The adversarial learning part of DLStudio now includes a WGAN implementation that
    uses Gradient Penalty for the learning required by the Critic.  All the changes
    made are in the AdversarialLearning class at the top level of the module.

  Version 2.1.1:

    In order to make it easier to navigate through the large code base of the module,
    I am adopting the convention that "Network" in the name of a class be reserved
    for only those cases when a class actually implements a network.  This convention
    requires that the name of an encapsulating class meant for teaching/learning a
    certain aspect of deep learning not contain "Network" in it.  Therefore, in
    Version 2.1.1, I have changed the names of the top-level classes
    AdversarialNetworks and Seq2SeqNetworks to AdversarialLearning and
    Seq2SeqLearning, respectively.

  Version 2.1.0:

    I have reorganized the code base a bit to make it easier for DLStudio to grow in
    the future.  This I did by moving the sequence-to-sequence learning (seq2seq)
    code to a separate module of the DLStudio platform.  The name of the new module
    is Seq2SeqLearning and it resides at the top level of the distribution.

  Version 2.0.9:

    With this version, DLStudio comes with educational material on
    sequence-to-sequence learning (seq2seq). To that end, I have included the
    following two new classes in DLStudio: (1) Seq2SeqWithLearnableEmbeddings for
    seq2seq with learnable embeddings; and (2) Seq2SeqWithPretrainedEmbeddings for
    doing the same with pre-trained embeddings. Although I have used word2vec for the
    case of pre-trained embeddings, you would be able to run the code with the
    Fasttext embeddings also.  Both seq2seq implementations include the attention
    mechanism based on my understanding of the original paper on the subject by
    Bahdanau, Cho, and Bengio. You will find this code in a class named
    Attention_BCB.  For the sake of comparison, I have also included an
    implementation of the the attention mechanism used in the very popular NLP
    tutorial by Sean Robertson.  You will find that code in a class named
    Attention_SR. To switch between these two attention mechanisms, all you have to
    do is to comment-out and uncomment a couple of lines in the DecoderRNN code.

  Version 2.0.8:

    This version pulls into DLStudio a very important idea in text processing and
    language modeling --- word embeddings.  That is, representing words by
    fixed-sized numerical vectors that are learned on the basis of their contextual
    similarities (meaning that if two words occur frequently in each other's context,
    they should have similar numerical representations).  Use of word embeddings is
    demonstrated in DLStudio through an inner class named
    TextClassificationWithEmbeddings.  Using pre-trained word2vec embeddings, this
    new inner class can be used for experimenting with text classification, sentiment
    analysis, etc.

  Version 2.0.7:

    Made incremental improvements to the visualization of intermediate results during
    training.

  Version 2.0.6:

    This is a result of further clean-up of the code base in DLStudio.  The basic
    functionality provided by the module has not changed.

  Version 2.0.5:

    This version has a bug-fix for the training loop used for demonstrating the power
    of skip connections.  I have also cleaned up how the intermediate results
    produced during training are displayed in your terminal window.  In addition, I
    deleted the part of DLStudio that dealt with Autograd customization since that
    material is now in my ComputationalGraphPrimer module.

  Version 2.0.4:

    This version mostly changes the HTML formatting of this documentation page.  The
    code has not changed.

  Version 2.0.3:

    I have been experimenting with how to best incorporate adversarial learning in
    the DLStudio platform. That's what accounts for the jump from the previous public
    release version 1.1.4 to new version 2.0.3.  The latest version comes with a
    separate class named AdversarialLearning for experimenting with different types
    of such networks for learning data models with adversarial learning and,
    subsequently, generating new instances of the data from the learned models. The
    AdversarialLearning class includes two Discriminator-Generator (DG) pairs and one
    Critic-Generator (CG) pair. Of the two DG pairs, the first is based on the logic
    of DCGAN, and the second a small modification of the first.  The CG pair is based
    on the logic of Wasserstein GAN.  This version of the module also comes with a
    new examples directory, ExamplesAdversarialLearning, that contains example
    scripts that show how you can call the different DG and CG pairs in the
    AdversarialLearning class.  Also included is a new dataset I have created,
    PurdueShapes5GAN-20000, that contains 20,000 images of size 64x64 for
    experimenting with the GANs in this module.

  Version 1.1.4:

    This version has a new design for the text classification class TEXTnetOrder2.
    This has entailed new scripts for training and testing when using the new version
    of that class. Also includes a fix for a bug discovered in Version 1.1.3

  Version 1.1.3:

    The only change made in this version is to the class GRUnet that is used for text
    classification.  In the new version, the final output of this network is based on
    the LogSoftmax activation.

  Version 1.1.2:

    This version adds code to the module for experimenting with recurrent neural
    networks (RNN) for classifying variable-length text input. With an RNN, a
    variable-length text input can be characterized with a hidden state vector of a
    fixed size.  The text processing capabilities of the module allow you to compare
    the results that you may obtain with and without using a GRU. For such
    experiments, this version also comes with a text dataset based on an old archive
    of product reviews made available by Amazon.

  Version 1.1.1:

    This version fixes the buggy behavior of the module when using the 'depth'
    parameter to change the size of a network.

  Version 1.1.0:

    The main reason for this version was my observation that when the training data
    is intentionally corrupted with a high level of noise, it is possible for the
    output of regression to be a NaN (Not a Number).  In my testing at noise levels
    of 20%, 50%, and 80%, while you do not see this problem when the noise level is
    20%, it definitely becomes a problem when the noise level is at 50%.  To deal
    with this issue, this version includes the test 'torch.isnan()' in the training
    and testing code for object detection.  This version of the module also provides
    additional datasets with noise corrupted images with different levels of noise.
    However, since the total size of the datasets now exceeds the file-size limit at
    'https://pypi.org', you'll need to download them separately from the link
    provided in the main documentation page.

  Version 1.0.9:

    With this version, you can now use DLStudio for experiments in semantic
    segmentation of images.  The code added to the module is in a new inner class
    that, as you might guess, is named SemanticSegmentation.  The workhorse of this
    inner class is a new implementation of the famous Unet that I have named mUNet
    --- the prefix "m" stands for "multi" for the ability of the network to segment
    out multiple objects simultaneously.  This version of DLStudio also comes with a
    new dataset, PurdueShapes5MultiObject, for experimenting with mUNet.  Each image
    in this dataset contains a random number of selections from five different shapes
    --- rectangle, triangle, disk, oval, and star --- that are randomly scaled,
    oriented, and located in each image.

  Version 1.0.7:

    The main reason for creating this version of DLStudio is to be able to use the
    module for illustrating how to simultaneously carry out classification and
    regression (C&R) with the same convolutional network.  The specific C&R problem
    that is solved in this version is the problem of object detection and
    localization. You want a CNN to categorize the object in an image and, at the
    same time, estimate the bounding-box for the detected object. Estimating the
    bounding-box is referred to as regression.  All of the code related to object
    detection and localization is in the inner class DetectAndLocalize of the main
    module file.  Training a CNN to solve the detection and localization problem
    requires a dataset that, in addition to the class labels for the objects, also
    provides bounding-box annotations for the objects.  Towards that end, this
    version also comes with a new dataset called PurdueShapes5.  Another new inner
    class, CustomDataLoading, that is also included in Version 1.0.7 has the
    dataloader for the PurdueShapes5 dataset.

  Version 1.0.6:

    This version has the bugfix for a bug in SkipBlock that was spotted by a student
    as I was demonstrating in class the concepts related to the use of skip
    connections in deep neural networks.

  Version 1.0.5:

    This version includes an inner class, BMEnet, for experimenting with skip
    connections to improve the performance of a deep network.  The Examples
    subdirectory of the distribution includes a script,
    playing_with_skip_connections.py, that demonstrates how you can experiment with
    skip connections in a network.

  Version 1.0.4:

    I have added one more inner class, AutogradCustomization, to the module that
    illustrates how to extend Autograd if you want to endow it with additional
    functionality. And, most importantly, this version fixes an important bug that
    caused wrong information to be written out to the disk when you tried to save the
    learned model at the end of a training session. I have also cleaned up the
    comment blocks in the implementation code.

  Version 1.0.3:

    This is the first public release version of this module.


@tag_intro
INTRODUCTION:

    DLStudio is an integrated software platform for teaching (and learning) a wide
    range of basic architectural features of deep-learning neural networks.

    To get the most educational value out of DLStudio, please see the slides for my
    lectures at Purdue's Deep Learning class.  Most of the learning you do with
    DLStudio is through the scripts in the various Example directories in the
    distribution.  To get access to these Example directories, please do NOT do "sudo
    pip install" on this module since that only gives you the main module files.  You
    would need to install it from the tar archive according to the installation
    instructions in this documentation page.
 
    As to why you may find DLStudio useful for your learning, note that most
    instructors who teach deep learning ask their students to download the so-called
    famous networks from, say, GitHub and become familiar with them by running them
    on the datasets used by the authors of those networks.  This approach is akin to
    teaching automobile engineering by asking the students to take the high-powered
    cars of the day out for a test drive.  In my opinion, this rather commonly used
    approach does not work for instilling in the students a deep understanding of the
    issues related to network architectures.

    Most instructors who teach deep learning ask their students to download the
    so-called famous networks from, say, GitHub and become familiar with them by
    running them on the datasets used by the authors of those networks.  This
    approach is akin to teaching automobile engineering by asking the students to
    take the high-powered cars of the day out for a test drive.  In my opinion, this
    rather commonly used approach does not work for instilling in the students a deep
    understanding of the issues related to network architectures.

    On the other hand, DLStudio offers its own implementations for a variety of key
    features of neural network architectures.  These implementations, along with
    their explanations through detailed slide presentations at our Deep Learning
    class website at Purdue, result in an educational framework that is much more
    efficient in what it can deliver within the time constraints of a single
    semester.

    DLStudio facilitates learning through a combination of inner classes of the main
    module class --- called DLStudio naturally --- and several additional modules in
    the overall platform.  These modules deal with Adversarial Learning, Metric
    Learning, Variational Autoencoding, Diffusion, Data Prediction, Text Analytics,
    Transformer based learning, etc.

    For the most part, the common code that you'd need in different scenarios for
    using neural networks has been placed inside the definition of the main DLStudio
    class in a file named DLStudio.py in the distribution.  That makes more compact
    the definition of the other inner classes within DLStudio. And, to a certain
    extent, that also results in a bit more compact code in the different modules in
    the DLStudio platform.


@tag2_skip
    SKIP CONNECTIONS:

    You can use DLStudio's inner class BMEnet to experiment with connection skipping
    in a deep network. Connection skipping means to provide shortcuts in a
    computational graph around the commonly used network components like
    convolutional and other types of layers.  In the absence of such shortcuts, deep
    networks suffer from the problem of vanishing gradients that degrades their
    performance.  Vanishing gradients means that the gradients of the loss calculated
    in the early layers of a network become increasingly muted as the network becomes
    deeper.  An important mitigation strategy for addressing this problem consists of
    creating a CNN using blocks with skip connections.

    As shown in the script playing_with_skip_connections.py in the Examples directory
    of the distribution, you can easily create a CNN with arbitrary depth just by
    using the constructor option "depth" for BMEnet. The basic block of the network
    constructed in this manner is called SkipBlock which, very much like the
    BasicBlock in ResNet-18, has a couple of convolutional layers whose output is
    combined with the input to the block.

    Note that the value given to the "depth" constructor option for the BMEnet class
    does NOT translate directly into the actual depth of the CNN. [Again, see the
    script playing_with_skip_connections.py in the Examples directory for how to use
    this option.] The value of "depth" is translated into how many instances of
    SkipBlock to use for constructing the CNN.

    If you want to use DLStudio for learning how to create your own versions of
    SkipBlock-like shortcuts in a CNN, your starting point should be the following
    script in the Examples directory of the distro:

                playing_with_skip_connections.py

    This script illustrates how to use the inner class BMEnet of the module for
    experimenting with skip connections in a CNN. As the script shows, the
    constructor of the BMEnet class comes with two options: skip_connections and
    depth.  By turning the first on and off, you can directly illustrate in a
    classroom setting the improvement you can get with skip connections.  And by
    giving an appropriate value to the "depth" option, you can show results for
    networks of different depths.


@tag2_detect
    OBJECT DETECTION AND LOCALIZATION:

    The code for how to solve the problem of object detection and localization with a
    CNN is in the inner classes DetectAndLocalize and CustomDataLoading.  This code
    was developed for version 1.0.7 of the module.  In general, object detection and
    localization problems are more challenging than pure classification problems
    because solving the localization part requires regression for the coordinates of
    the bounding box that localize the object.  If at all possible, you would want
    the same CNN to provide answers to both the classification and the regression
    questions and do so at the same time.  This calls for a CNN to possess two
    different output layers, one for classification and the other for regression.  A
    deep network that does exactly that is illustrated by the LOADnet classes that
    are defined in the inner class DetectAndLocalize of the DLStudio platform.  [By
    the way, the acronym "LOAD" in "LOADnet" stands for "LOcalization And
    Detection".] Although you will find three versions of the LOADnet class inside
    DetectAndLocalize, for now only pay attention to the LOADnet2 class since that is
    the one I have worked with the most for creating the 1.0.7 distribution.

    As you would expect, training a CNN for object detection and localization
    requires a dataset that, in addition to the class labels for the images, also
    provides bounding-box annotations for the objects in the images. Out of my great
    admiration for the CIFAR-10 dataset as an educational tool for solving
    classification problems, I have created small-image-format training and testing
    datasets for illustrating the code devoted to object detection and localization
    in this module.  The training dataset is named PurdueShapes5-10000-train.gz and
    it consists of 10,000 images, with each image of size 32x32 containing one of
    five possible shapes --- rectangle, triangle, disk, oval, and star. The shape
    objects in the images are randomized with respect to size, orientation, and
    color.  The testing dataset is named PurdueShapes5-1000-test.gz and it contains
    1000 images generated by the same randomization process as used for the training
    dataset.  You will find these datasets in the "data" subdirectory of the
    "Examples" directory in the distribution.

    Providing a new dataset for experiments with detection and localization meant
    that I also needed to supply a custom dataloader for the dataset.  Toward that
    end, Version 1.0.7 also includes another inner class named CustomDataLoading
    where you will my implementation of the custom dataloader for the PurdueShapes5
    dataset.

    If you want to use DLStudio for learning how to write your own PyTorch code for
    object detection and localization, your starting point should be the following
    script in the Examples directory of the distro:

                object_detection_and_localization.py

    Execute the script and understand what functionality of the inner class
    DetectAndLocalize it invokes for object detection and localization.


@tag2_noisy
    NOISY OBJECT DETECTION AND LOCALIZATION:

    When the training data is intentionally corrupted with a high level of noise, it
    is possible for the output of regression to be a NaN (Not a Number).  Here is
    what I observed when I tested the LOADnet2 network at noise levels of 20%, 50%,
    and 80%: At 20% noise, both the labeling and the regression accuracies become
    worse compared to the noiseless case, but they would still be usable depending on
    the application.  For example, with two epochs of training, the overall
    classification accuracy decreases from 91% to 83% and the regression error
    increases from under a pixel (on the average) to around 3 pixels.  However, when
    the level of noise is increased to 50%, the regression output is often a NaN (Not
    a Number), as presented by 'numpy.nan' or 'torch.nan'.  To deal with this
    problem, Version 1.1.0 of the DLStudio platform checks the output of the
    bounding-box regression before drawing the rectangles on the images.

    If you wish to experiment with detection and localization in the presence of
    noise, your starting point should be the script

                noisy_object_detection_and_localization.py

    in the Examples directory of the distribution.  Note that you would need to
    download the datasets for such experiments directly from the link provided near
    the top of this documentation page.


@tag2_diou
    IoU REGRESSION FOR OBJECT DETECTION AND LOCALIZATION:

    Starting with version 2.2.3, DLStudio illustrates how you can use modern variants
    of the IoU (Intersection over Union) loss function for the regression needed for
    object localization.  These loss functions are provided by the DIoULoss class
    that is a part of DLStudio's inner class DetectAndLocalize. If you wish to
    experiment with these loss functions, you best entry point would be the script

                object_detection_and_localization_iou.py

    in the Examples directory of the distribution.  This script uses the same
    PurdueShapes5-10000-train.gz and PurdueShapes5-1000-test.gz training and testing
    datasets as the object_detection_and_localization.py script mentioned earlier.


@tag2_semantic
    SEMANTIC SEGMENTATION:

    The code for how to carry out semantic segmentation is in the inner class that is
    appropriately named SemanticSegmentation.  At its simplest, the purpose of
    semantic segmentation is to assign correct labels to the different objects in a
    scene, while localizing them at the same time.  At a more sophisticated level, a
    system that carries out semantic segmentation should also output a symbolic
    expression that reflects an understanding of the scene in the image that is based
    on the objects found in the image and their spatial relationships with one
    another.  The code in the new inner class is based on only the simplest possible
    definition of what is meant by semantic segmentation.
    
    The convolutional network that carries out semantic segmentation DLStudio is
    named mUNet, where the letter "m" is short for "multi", which, in turn, stands
    for the fact that mUNet is capable of segmenting out multiple object
    simultaneously from an image.  The mUNet network is based on the now famous Unet
    network that was first proposed by Ronneberger, Fischer and Brox in the paper
    "U-Net: Convolutional Networks for Biomedical Image Segmentation".  Their UNET
    extracts binary masks for the cell pixel blobs of interest in biomedical images.
    The output of UNET can therefore be treated as a pixel-wise binary classifier at
    each pixel position.  The mUNet class, on the other hand, is intended for
    segmenting out multiple objects simultaneously form an image. [A weaker reason
    for "m" in the name of the class is that it uses skip connections in multiple
    ways --- such connections are used not only across the two arms of the "U", but
    also also along the arms.  The skip connections in the original Unet are only
    between the two arms of the U.

    mUNet works by assigning a separate channel in the output of the network to each
    different object type.  After the network is trained, for a given input image,
    all you have to do is examine the different channels of the output for the
    presence or the absence of the objects corresponding to the channel index.

    This version of DLStudio also comes with a new dataset,
    PurdueShapes5MultiObject, for experimenting with mUNet.  Each image in this
    dataset contains a random number of selections from five different shapes,
    with the shapes being randomly scaled, oriented, and located in each image.
    The five different shapes are: rectangle, triangle, disk, oval, and star.

    Your starting point for learning how to use the mUNet network for segmenting
    images should be the following script in the Examples directory of the distro:

                semantic_segmentation.py

    Execute the script and understand how it uses the functionality packed in the
    inner class SemanticSegmentation for segmenting out the objects in an image.


@tag2_vae
    VARIATIONAL AUTO-ENCODNG (VAE):

    Starting with Version 2.5.1, you can experiment with generative autoencoding in
    the DLStudio platform.  The inner class of DLStudio that allows you to do that is
    called VAE (for Variational Auto-Encoding).  Generative data modeling with
    variational autoencoding is based on the assumption that exists a relatively
    simple Latent Space that captures the essence of what's in the images you are
    interested in.  That is, it is possible to map any given input image to a
    low-dimensional (relatively speaking) vector z that can be modeled with a simple
    probabilty distribution (which, ideally speaking, would be a zero-mean,
    unit-covariance Gaussian) that could subseqently be used to generate useful
    variants of the input image.

    A great thing about VAE is that it allows you to carry out what's known as
    disentanglement learning in which the learned latent space captures the essence
    of each image in your training dataset and have the Decoder capture the rest.
    (The Encoder's job is to map the input image to its representation in the Latent
    Space.)

    I have implemented variational autoencoding in DLStudio through a base class
    Autoencoder and a derived class VAE. Both of these are inner classes of the main
    DLStudio class. (That is, both these classea are defined in the file
    "DLStudio.py" in the distribution.) It is the Encoder and the Decoder in the base
    class Autoencoder that does the bulk of computing in VAE. What the VAE class does
    specifically is to feed the output of Autoencoder's Encoder into two nn.Linear
    layers for the learning of the mean and the log-variance of the latent
    distribution for the training dataset.  Regarding decoding, VAE's Decoder invokes
    what's known as the "reparameterization trick" for sampling the latent
    distribution to first construct a sample from the latent space, reshape the
    sample appropriately, and to then feed it into Autoencoder's Decoder.

    If you want to experiment with autoencoding and variational autoencoding in
    DLStudio, your staring points should be the following three scripts in the
    Examples directory of the distribution:

               run_autoencoder.py
               run_vae.py
               run_vae_for_image_generation.py

    The first script, run_autoencoder.py, is for experimenting with just the
    Autoencoder class by itself.  For example, if you wanted to experiment with
    dimensionality reduction with an Autoencoder, all you would need to do would be
    to change the last or the last couple of layers of the Decoder in the Autoencoder
    class and see for yourself the results by running this script.  The second
    script, run_vae.py, is for experimenting with the variational autoencoding code
    in the VAE class. And the last script, run_vae_for_image_generation.py, is for
    experimenting with just the Decoder part of the VAE class.  The VAE Decoder is in
    reality a Generator that samples a Gaussian probability distribution, as
    specified by its mean and covariance, and transforms the sample back into an
    image that, ideally speaking, should belong to the same distribution as the
    images used for training the VAE.


@tag2_vaevq
    VAE WITH CODEBOOK LEARNING (VQVAE and VQGAN):

    The development of VQVAE brought us what's now known as the Codebook Learning in
    Deep Learning that eventually placed languages and images on an equal footing
    with regard to attention-based processing with transformers.  The prefix "VQ"
    stands for "Vector Quantization" that replaces each vector produced by the
    Encoder (the values in the vector lie along the channel dimension at the output
    of an Encoder) by the closest similar vector in a learned codebook.  This act
    suppresses noise and other irrelevant variations at the Encoder output.

    VQVAE does three things: (1) If the output of the Encoder is of shape NxNxC, it
    is re-imagined as representing the input image with N^2 embedding vectors, each
    of dimensionality C. (2) You declare a Codebook consisting of K vectors, each of
    dimensionality, again, C. And, finally, (3) You replace each embedding vector at
    the output of the Encoder with its closest Codebook vector. Finally, you feed the
    "reconstituted" embedding vectors into the Decoder to recover an image (or its
    desired variants in a conditional implementation).

    VQGAN goes one step further by showing that the Codebook vectors in a VQVAE can
    be treated like the embedding vectors associated with the tokens in transformer-
    based neural architectures for language processing.  The token sequences for such
    transformer based processing would consist of the integer indices associated with
    the Codebook vectors that an input image is mapped to. The original authors of
    VQGAN have demonstrated that such networks can generate virtual image variants of
    training images, with the virtual images being larger in size and of greater
    visual complexity than was possible before.

    To learn these ideas through DLStudio, please note the following scripts in the
    Examples directory of the distribution:    

             run_vqvae.py

             run_vqgan.py

             run_vqgan_map_image_to_codebook.py

             run_vqgan_transformer.py

    The script "run_vqvae.py" stands on its own and try to play with it in order to
    learn the basics of codebook learning.  

    The following two scripts named above:

             run_vqgan.py

             run_vqgan_transformer.py

    are two parts of what it takes to accomplish the following: autoregressive
    modeling of the images through the tokens that correspond to the vectors in the
    learned Codebook.  You first work with "run_vqgan.py" to train the Encoder, the
    Decoder, and the VectorQuantizer networks.  Subsequently, using the components
    trained by "run_vqgan.py", you work with "run_vqgan_transformer.py" in order to
    train a transformer network for autoregressive modeling of the images.

    On the four scripts named above, that leaves

             run_vqgan_map_image_to_codebook.py

    is specifically for you to acquire deeper intuitions about what exactly in the
    images is represented by the Codebook vectors.  In order to play with this
    script, you MUST first run the script "run_vqgan.py" for training the VQGAN
    network.  Subsequently, playing with "run_vqgan_map_image_to_codebook.py" will
    help you better understand the role played by the Codebook vectors in the output
    produced by the Decoder.  For additional information related to this script, see
    the comment block at the top of the file in the Examples directory of the
    distribution.


@tag2_text
    TEXT CLASSIFICATION:

    Starting with Version 1.1.2, the module includes an inner class
    TextClassification that allows you to do simple experiments with neural
    networks with feedback (that are also called Recurrent Neural Networks).  With
    an RNN, textual data of arbitrary length can be characterized with a hidden
    state vector of a fixed size.  To facilitate text based experiments, this
    module also comes with text datasets derived from an old Amazon archive of
    product reviews.  Further information regarding the datasets is in the comment
    block associated with the class SentimentAnalysisDataset. If you want to use
    DLStudio for experimenting with text, your starting points should be the
    following three scripts in the Examples directory of the distribution:

                text_classification_with_TEXTnet.py
                text_classification_with_TEXTnetOrder2.py
                text_classification_with_GRU.py

    The first of these is meant to be used with the TEXTnet network that does not
    include any protection against the vanishing gradients problem that a poorly
    designed RNN can suffer from.  The second script mentioned above is based on
    the TEXTnetOrder2 network and it includes rudimentary protection, but not
    enough to suffice for any practical application.  The purpose of TEXTnetOrder2
    is to serve as an educational stepping stone to a GRU (Gated Recurrent Unit)
    network that is used in the third script listed above.

    Starting with Version 2.0.8, the Examples directory of DLStudio also includes
    the following three scripts that use the same learning networks as the
    corresponding scripts mentioned above but with word representations based on
    word2vec embeddings:

                text_classification_with_TEXTnet_word2vec.py
                text_classification_with_TEXTnetOrder2_word2vec.py
                text_classification_with_GRU_word2vec.py

    The pre-trained word2vec embeddings used in these scripts are accessed
    through the popular gensim library.


@tag2_adversarial
    DATA MODELING WITH ADVERSARIAL LEARNING:

    Starting with version 2.0.3, DLStudio includes a separate module named
    AdversarialLearning for experimenting with different adversarial learning
    approaches for data modeling.  Adversarial Learning consists of simultaneously
    training a Generator and a Discriminator (or, a Generator and a Critic) with
    the goal of getting the Generator to produce from pure noise images that look
    like those in the training dataset.  When Generator-Discriminator pairs are
    used, the Discriminator's job is to become an expert at recognizing the
    training images so it can let us know when the generator produces an image
    that does not look like what is in the training dataset.  The output of the
    Discriminator consists of the probability that the input to the discriminator
    is like one of the training images.

    On the other hand, when a Generator-Critic pair is used, the Critic's job is
    to become adept at estimating the distance between the distribution that
    corresponds to the training dataset and the distribution that has been learned
    by the Generator so far.  If the distance between the distributions is
    differentiable with respect to the weights in the networks, one can backprop
    the distance and update the weights in an iterative training loop.  This is
    roughly the idea of the Wasserstein GAN that is incorporated as a
    Critic-Generator pair CG1 in the AdversarialLearning class.

    The AdversarialLearning class includes two kinds of adversarial networks for
    data modeling: DCGAN and WGAN.

    DCGAN is short for "Deep Convolutional Generative Adversarial Network", owes
    its origins to the paper "Unsupervised Representation Learning with Deep
    Convolutional Generative Adversarial Networks" by Radford et al.  DCGAN was
    the first fully convolutional network for GANs (Generative Adversarial
    Network). CNN's typically have a fully-connected layer (an instance of
    nn.Linear) at the topmost level.  For the topmost layer in the Generator
    network, DCGAN uses another convolution layer that produces the final output
    image.  And for the topmost layer of the Discriminator, DCGAN flattens the
    output and feeds that into a sigmoid function for producing scalar value.
    Additionally, DCGAN also gets rid of max-pooling for downsampling and instead
    uses convolutions with strides.  Yet another feature of a DCGAN is the use of
    batch normalization in all layers, except in the output layer of the Generator
    and the input layer of the Discriminator.  As the authors of DCGAN stated,
    while, in general, batch normalization stabilizes learning by normalizing the
    input to each layer to have zero mean and unit variance, applying BN at the
    output results in sample oscillation and model instability.  I have also
    retained in the DCGAN code the leaky ReLU activation recommended by the
    authors for the Discriminator.

    The other adversarial learning framework incorporated in AdversarialLearning
    is based on WGAN, which stands for Wasserstein GAN.  This GAN was proposed in
    the paper "Wasserstein GAN" by Arjovsky, Chintala, and Bottou.  WGANs is based
    on estimating the Wasserstein distance between the distribution that
    corresponds to the training images and the distribution that has been learned
    so far by the Generator.  The authors of WGAN have shown that minimizing this
    distance in an iterative learning framework also involves solving a minimax
    problem involving a Critic and a Generator. The Critic's job is to become an
    expert at recognizing the training data while, at the same time, distrusting
    the output of the Generator. Unlike the Discriminator of a GAN, the Critic
    merely seeks to estimate the Wasserstein distance between the true
    distribution associated with the training data and the distribution being
    learned by the Generator.  As the Generator parameters are kept fixed, the
    Critic seems to update its parameters that maximize the Wasserstein distance
    between the true and the fake distributions. Subsequently, as the Critic
    parameters are kept fixed, the Generator updates its learnable parameters in
    an attempt to minimize the same distance.

    Estimation of the Wasserstein distance in the above logic requires for the
    Critic to learn a 1-Lipschitz function. DLStudio implements the following two
    strategies for this learning:

        --  Clipping the values of the learnable parameters of the Critic network
            to a user-specified interval;

        --  Penalizing the gradient of the norm of the Critic with respect to its
            input.

    The first of these is implemented in the function "run_gan_code()" in the file
    AdversarialLearning.py and the second in the function
    "run_wgan_with_gp_code()" in the same file.

    If you wish to use the DLStudio platform to learn about data modeling with
    adversarial learning, your entry points should be the following scripts in the
    ExamplesAdversarialLearning directory of the distro:

        1.  dcgan_DG1.py            

        2.  dcgan_DG2.py   

        3.  wgan_CG1.py             

        4.  wgan_with_gp_CG2.py

    The first script demonstrates the DCGAN logic on the PurdueShapes5GAN dataset.
    In order to show the sensitivity of the basic DCGAN logic to any variations in
    the network or the weight initializations, the second script introduces a
    small change in the network.  The third script is a demonstration of using the
    Wasserstein distance for data modeling through adversarial learning. The
    fourth script includes a gradient penalty in the critic logic called on by the
    third script.  The results produced by these scripts (for the constructor
    options shown in the scripts) are included in a subdirectory named
    RVLCloud_based_results.


@tag2_diffusion
    DATA MODELING WITH DIFFUSION:

    Starting with Version 2.4.2, DLStudio includes a new module named
    GenerativeDiffusion for experimenting with what's known as "Denoising Diffusion".
    The Denoising Diffusion approach to data modeling is based on the interaction
    between two Markov Chains over T timesteps: A forward chain called the q-chain
    and a reverse chain called the p-chain.  

    At each timestep in the forward q-chain, the data coursing through the chain is
    subject to a Markov transition that injects a small amount of zero-mean and
    isotropic Gaussian noise into the data. The goal in the q-chain is to inject
    sufficient noise at each timestep so that, at the end of the T timesteps, one
    will end up with pure isotropic noise.

    On the other hand, the goal in the reverse p-chain, is to start with zero-mean
    isotropic noise, subject it to a denoising Markov transition that gets rid of
    a bit of the noise in the input, do so at every timestep, until you have
    recovered a recognizable image at the end of the chain.

    While the amount of noise that is injected into the data at each transition in
    the forward q-chain is set by the user, how much denoising to carry out at the
    corresponding transition in the reverse p-chain is determined by a neural
    network whose job is to estimate the amount of denoising that, in a sense,
    would be "exact" opposite of the extent of diffusion carried at the
    corresponding transition in the forward q-chain.

    The computational scenario described above becomes particularly tractable for
    the case when you use isotropic Gaussian noise for both diffusion and
    denoising. When the transition probability at each timestep is isotropic
    Gaussian in the forward q-chain, it is easy to show that one can combine an
    arbitrary number of timesteps and get to the target timestep in a single hop.
    This leads to a particularly efficient algorithm described below for training
    the denoising neural network whose job is merely to estimate the best
    denoising transitions at each timestep:

    --- At each iteration of training the neural network, randomly choose a timestep
        t from the range that consists of T timesteps.

    --- Apply a single cumulative q-chain transition to the input training image
        that would be equivalent to taking the input image through t consecutive
        transitions in the q-chain.

    --- For each q-chain transition to the timestep t, use the Bayes' Rule to estimate
        the posterior probability q( x_{t-1} | x_t, x_0 ) from the Markov transition
        probability q( x_t | x0, x_{t-1} ).

    --- Use the posterior probabilities mentioned above as the target for training
        the neural network whose job is to estimate the transition probability p(
        x_{t-1} | x_t ) in the reverse p-chain.  The loss function for training
        the neural network could be the KL-Divergence between the posterior q(
        x_{t-1} | x_t, x_0 ) and the predicted p( x_{t-1} | x_t ).

        Another possibility for the loss would be the MSE error between the
        isotropic noise that was injected in the q-chain transition in question
        and the prediction of the same in the p-chain by using the posterior
        estimates for the mean and the variance using the transition probability
        p( x_{t-1} | x_t ) predicted by the neural network.

        Yet another possibility is to directly form an estimate for the input
        image x_0 using the above-mentioned posterior estimates for the mean and
        the variance and then construct an MSE loss based on the difference
        between the estimated x_0 and its true value.
        
    As should be clear from the above description, the sole goal of training the
    neural network is to make it an expert at the prediction of the denoising
    transition probabilities p( x_{t-1} | x_t ).  Typically, you carry out the
    training in an infinite loop while spiting out the checkpoints every so often.

    When you are ready to see the image generation power of a checkpoint, you
    start with isotropic Gaussian noise as the input and take it through all of
    the T timestep p-chain transitions that should lead to a recognizable image.
    
    The ExamplesDiffusion directory of DLStudio contains the following files that
    you will find helpful for your experiments with diffusion:

       0.  README

       1.  RunCodeForDiffusion.py

       2.  GenerateNewImageSamples.py

       3.  VisualizeSamples.py

    Any experiment with diffusion will involve all three scripts mentioned above.
    The script RunCodeForDiffusion.py is for training the neural network to become
    adept at learning the p-chain transition probabilities p( x_{t-1} | x_t ).
    The script GenerateNewImageSamples.py is for generating the images using the
    learned model.  This script deposits all the generated images in a numpy
    archive for ndarrays.  The last script, VisualizeSamples.py, is for extracting
    the individual images from that archive.  Please make sure that you have gone
    through the README mentioned above before starting your experiments with the
    diffusion part of DLStudio.
 

@tag2_seq2seq
    SEQUENCE-TO-SEQUENCE LEARNING WITH ATTENTION

    Sequence-to-sequence learning (seq2seq) is about predicting an outcome
    sequence from a causation sequence, or, said another way, a target sequence
    from a source sequence.  Automatic machine translation is probably one of the
    most popular applications of seq2seq.  DLStudio uses English-to-Spanish
    translation to illustrate the programming idioms and the PyTorch structures
    you need for seq2seq.  To that end, Version 2.1.0 of DLStudio includes a
    new module named Seq2SeqLearning that consists of the following two 
    demonstration classes:

        1.  Seq2SeqWithLearnableEmbeddings

        2.  Seq2SeqWithPretrainedEmbeddings

    As their names imply, the first is for seq2seq with learnable embeddings and
    the second for seq2seq with pre-trained embeddings like word2vec or fasttext.

    As mentioned above, the specific example of seq2seq addressed in my
    implementation code is translation from English to Spanish. (I chose this
    example because learning and keeping up with Spanish is one of my hobbies.)
    In the Seq2SeqWithLearnableEmbeddings class, the learning framework learns the
    best embedding vectors to use for the two languages involved. On the other
    hand, in the Seq2SeqWithPretrainedEmbeddings class, I use the word2vec
    embeddings provided by Google for the source language.  As to why I use the
    pre-training embeddings for just the source language is explained in the main
    comment doc associated with the class Seq2SeqWithPretrainedEmbeddings.

    Any modern attempt at seq2seq must include attention.  This is done by
    incorporating a separate Attention network in the Encoder-Decoder framework
    needed for seq2seq learning.  The goal of the attention network is to modify
    the current hidden state in the decoder using the attention units produced
    previously by the encoder for the source language sentence.  The main
    Attention model I have used is based on my understanding of the attention
    mechanism proposed by Bahdanau, Cho, and Bengio. You will see this attention
    code in a class named Attention_BCB in the seq2seq implementations named
    above. I have also provided another attention class named Attention_SR that is
    my implementation of the attention mechanism in the very popular NLP tutorial
    by Sean Robertson at the PyTorch website.  The URLs to both these attention
    mechanisms are in my Week 14 lecture material on deep learning at Purdue.

    The following two scripts in the ExamplesSeq2SeqLearning directory are your
    main entry points for experimenting with the seq2seq code in DLStudio:

        1.  seq2seq_with_learnable_embeddings.py

        2.  seq2seq_with_pretrained_embeddings.py
    
    With the first script, the overall network will learn on its own the best
    embeddings to use for representing the words in the two languages.  And, with
    the second script, the pre-trained word2vec embeddings from Google are used
    for the source language while the system learns the embeddings for the target
    language.


@tag2_predict
    DATA PREDICTION

    Let's say you have a sequence of observations recorded at regular intervals.
    These could, for example, be the price of a stock share recorded every hour;
    the hourly recordings of electrical load at your local power utility company;
    the mean average temperature recorded on an annual basis; and so on.  We want
    to use the past observations to predict the value of the next one.  Solving
    these types of problems is the focus of the DataPrediction module in the
    DLStudio platform.

    As a problem, data prediction has much in common with text analytics and
    seq2seq processing, in the sense that the prediction at the next time instant
    must be based on the previous observations in a manner similar to what we do
    in text analytics where the next word is understood taking into account all
    the previous words in a sentence.  However, there are three significant
    differences between purely numerical data prediction problems and text-based
    problems:

    1) Data Normalization: As you know by this time, neural networks require that
       your input data be normalized to the [0,1] interval, assuming it consists
       of non-negative numbers, or the [-1,1] interval otherwise.  When solving a
       sequential-data problem like text analytics, after you have normalized the
       input data (which is likely to consist of the numeric embeddings for the
       input words), you can forget about it.  You don't have that luxury when
       solving a data prediction problem.  As you would expect, the next value
       predicted by an algorithm must be at the same scale as the original input
       data.  This requires that the output of a neural-network-based prediction
       algorithm must be "inverse normalized".  And that, in turn, requires
       remembering the normalization parameters used in each channel of the input
       data.

    2) Input Data Chunking: The notion of a sentence that is important in text
       analytics does not carry over to the data prediction problem.  In general,
       you would want a prediction to be made using ALL of the past
       observations. When the sequential data available for training a predictor
       is arbitrarily long, as is the case with numerical data in general, you
       would need to decide how to "chunk" the data --- that is, how to extract
       sub-sequences from the data for the purpose of training a neural network.

    3) Datetime Conditioning: Time-series data typically includes a "datetime"
       stamp for each observation.  Representing datetime as a one-dimensional
       ever-increasing time value does not work for data prediction if the
       observations depend on the time of the day, the day of the week, the season
       of the year, and other such temporal effects.  Incorporating such effects
       in a prediction framework requires a multi-dimensional encoding of the
       datetime values.  See the doc page associated with the DataPrediction class
       for a longer explanation of this aspect of data prediction.

    Now that you understand how the data prediction problem differs from, say, the
    problem of text analytics, it is time for me to state my main goal in defining
    the DataPrediction module in the DLStudio platform.  I actually have two
    goals:

    (a) To deepen your understanding of a GRU.  At this point, your understanding
        of a GRU is likely to be based on calling PyTorch's GRU in your own code.
        Using a pre-programmed implementation for a GRU makes life easy and you
        also get a piece of highly optimized code that you can just call in your
        own code.  However, with a pre-programmed GRU, you are unlikely to get
        insights into how such an RNN is actually implemented.

    (b) To demonstrate how you can use a Recurrent Neural Network (RNN) for data
        prediction taking into account the data normalization, chunking, and
        datetime conditioning issues mentioned earlier.

    To address the first goal above, the DataPrediction class presented in this
    file is based on my pmGRU (Poor Man's GRU).  This GRU is my implementation of
    the "Minimal Gated Unit" GRU variant that was first presented by Joel Heck and
    Fathi Salem in their paper "Simplified Minimal Gated Unit Variations for
    Recurrent Neural Networks".  Its hallmark is that it combines the Update and
    the Reset gates of a regular GRU into a single gate called the Forget Gate.
    You could say that pmGRU is a lightweight version of a regular GRU and its use
    may therefore lead to a slight loss of accuracy in the predictions.  You will
    find it educational to compare the performance you get with my pmGRU-based
    implementation with an implementation that uses PyTorch's GRU for the same
    dataset.

    Your main entry point for experimenting with the DataPrediction module is
    the following script in the ExamplesDataPrediction directory of the DLStudio
    distribution:

        power_load_prediction_with_pmGRU.py

    Before you can run this script, you would need to download the training
    dataset used in this example.  See the "For Data Prediction" part of the "The
    Datasets Included" section of the doc page for that.


@tag2_transformers
    TRANSFORMERS

    For Seq2SeqLearning learning, the goal of a Transformer based implementation
    is the same as described earlier in this Introduction except that now you
    completely forgo recurrence. That is, you only use the mechanism of attention
    to translate sentences from a source language into sentences in the target
    language. For such applications, you need two forms of attention:
    self-attention and cross-attention.  Self-attention refers to the
    intra-sentence relationships between the words and cross-attention refers to
    the inter-sentence relationships between the words in a pair of sentences, one
    in the source language and the other in the target language. I have explained
    these concepts in great detail in the doc sections of the inner classes in the
    Transformers class.  In particular, I have explained the concept of the
    "dot-product" attention in which each word puts out three things: a Query
    Vector Q, a Key Vector K, and a Value Vector V. By taking the dot-product of
    the Query Vector Q of a word with the Key Vector K for all the words in a
    sentence, the neural network gets a measure of the extent to which each word
    in a sentence is important to every other word.  These dot-product values are
    then used as weights on the Value Vectors, V, for the individual words.  Cross
    attention works in a similar manner, except that now you take the dot-products
    of the Q vectors in the target-language sentence with the K vectors in the
    corresponding source-language sentence for producing the weight vectors that
    tell us how to weight the source-language Value Vectors vis-a-vis the words in
    the target language.

    In addition to their use in Seq2SeqLearning learning, transformers are now
    also used widely in computer vision applications. As a nod to their adoption
    in the learning required for solving CV problems, I have created a new class
    named visTransformer in the Transformers module of DLStudio.  The transformer
    part of the logic in a visTransformer is identical to what it is in a
    transformer class for Seq2SeqLearning learning.  That logic kicks in after you
    have divided an image into patches and you represent each patch by an
    embedding vector --- in exactly the same as when you represent a word or a
    token in a sentence by an embedding vector.

    You will see three different implementations of the transformer architecture in
    the Transformers module of the DLStudio platform:

          TransformerFG

          TransformerPreLN

          visTransformer

    The "FG" suffix TransformerFG stands for "First Generation"; the "PreLN"
    suffix in TransformerPreLN for "Pre LayerNorm"; and, finally, the name
    visTransformer stands for "Vision Transformer."  

    TransformerFG is my implementation of the transformer architecture proposed in
    the famous paper by Vaswani et al.  and TransformerPreLN my implementation of
    the same architecture but with the modification suggested by Xiong et al. for
    more stable learning.  Since, the modification is small from an architectural
    standpoint, I could have combined both transformer types in the same
    implementation with some conditional logic to account for the differences.
    However, I have chosen to keep them separate mostly for educational purposes.
    Further details on these implementations are in the documentation blocks in
    the Transformers module.

    The visTransformer implementation is based on the paper "An Image is Worth
    16x16 Words: Transformers for Image Recognition at Scale'' by Dosovitskiy et
    al.
 
    If you want to use my code for learning the main ideas related to how to
    create purely attention based networks, your starting point for that should be
    the following scripts in the ExamplesTransformers directory of the DLStudio
    distribution:

        seq2seq_with_transformerFG.py
        seq2seq_with_transformerPreLN.py

    These scripts uses the following English-Spanish sentence-pairs dataset

           en_es_xformer_8_90000.tar.gz

    that contains 90,000 pairs of English-Spanish sentences with the maximum
    number of words in each sentence limited to 8 words.  For processing by the
    attention networks, each sentence is enclosed in <SOS> and <EOS> tokens, with
    the former standing for "Start of Sentence" and the latter for "End of
    Sentence".

    And if you wish to use visTransformer for solving image recognition problems
    with a transformer based implementation, your starting point should be
    the following scripts in the same ExamplesTransformers directory that was
    mentioned above:

          image_recog_with_visTransformer.py
          test_checkpoint_for_visTransformer.py 

    Both these script use the CIFAR10 dataset for demonstrating image recognition.


@tag2_metriclearning
    METRIC LEARNING

    The main idea of metric learning is to learn a mapping from the images to
    their embedding vector representations in such a way that the embeddings for
    what are supposed to be similar images are pulled together and those for
    dissimilar images are pulled as far apart as possible.  After such a mapping
    function is learned, you can take a query image (whose class label is not
    known), run it through the network to find its embedding vector, and,
    subsequently, assign to the query images the class label of the nearest
    training-image neighbor in the embedding space.  As explained in my Metric
    Learning lecture in the Deep Learning class at Purdue, this approach to
    classification is likely to work under data circumstances when the more neural
    network classifiers fail.

    Two commonly used loss functions for metric learning are Pairwise Contrastive
    Loss and Triplet Loss.  

    Pairwise Contrastive Loss is based on extracting all the Positive and the
    Negative Pairs of images form a batch.  For a Positive Pair, both the images
    in the pair must have the same label, and, for a Negative Pair, the two labels
    must be different.  A minimization of the Pairwise Contrastive Loss should
    decrease the distance between the embedding vectors for a Positive Pair and
    increase the distance between the embedding vectors for a Negative Pair.  If
    the two embeddings in a Negative Pair are already well separated, there would
    be no point to have them contribute to the loss calculation.  This is
    accomplished by incorporating the notion of a margin.  The idea is that we
    want to increase the distance between the two embeddings in a Negative Pair to
    the value specified by the Margin and no more. Should it be the case that two
    such embeddings are already separated by a distance greater than the Margin,
    we do not include such pairs in the loss calculation.

    Triplet Loss, on the other hand, starts with the notion of triplets (i,j,k) of
    the indices for triplets of images in a batch, with no two of the indices
    being the same. The image indexed by i is considered to be the Anchor in the
    triplet, the image indexed by j as Positive, and the one by k as the Negative.
    We also refer to such triplets with the notation (Anchor, Pos, Neg).  We again
    need the notion of a Margin. When we form the (Anchor, Pos, Neg) triplets from
    a batch, we focus on only those Neg images that are further away from the
    Anchor than the Pos image, but no farther than the (Anchor,Pos) distance plus
    the Margin.  Including the Negative images that are closer than the (Anchor,
    Pos) distance can make the learning unstable and including the Negatives that
    farther than the "(Anchor,Pos) plus the Margin" distance is likely to be
    wasteful.

    Forming set of Positive and Negative Pairs for the Pairwise Contrastive Loss
    and forming sets of Triplets for the Triplet Loss is referred to as Mining a
    batch.  This allows us to talk about concepts like "negative-hard mining",
    "negative semi-hard mining", etc., that depend on the relative distances
    between the images in the Negative Pairs and the distance of a negative
    vis-a-vis those in a Positive Pair.

    If you wish to use this module to learn about metric learning, your entry
    points should be the following scripts in the ExamplesMetricLearning directory
    of the distro:

        1.  example_for_pairwise_contrastive_loss.py

        2.  example_for_triplet_loss.py

    As the names imply, the first script demonstrates using the Pairwise
    Contrastive Loss for metric learning and the second script using the Triplet
    Loss for doing the same.  Both scripts can work with either the pre-trained
    ResNet-50 trunk model or the homebrewed network supplied with the
    MetricLearning module.


@tag_install
INSTALLATION:

    The DLStudio class was packaged using setuptools.  For installation, execute
    the following command in the source directory (this is the directory that
    contains the setup.py file after you have downloaded and uncompressed the
    package):
 
            sudo python3 setup.py install

    On Linux distributions, this will install the module file at a location that
    looks like

             /usr/local/lib/python3.10/dist-packages/

    If you do not have root access, you have the option of working directly off
    the directory in which you downloaded the software by simply placing the
    following statements at the top of your scripts that use the DLStudio class:

            import sys
            sys.path.append( "pathname_to_DLStudio_directory" )

    To uninstall DLStudio, simply delete the source code directory, locate where
    DLStudio was installed with "locate DLStudio" and delete those files.  As
    mentioned above, the full pathname to the installed version is likely to look
    like /usr/local/lib/python3.10/dist-packages/DLStudio*

    If you want to carry out a non-standard install of DLStudio, look up the
    on-line information on Disutils by pointing your browser to

              http://docs.python.org/dist/dist.html

@tag_usage
USAGE:

    If you want to specify a network with just a configuration string, your usage
    of the module is going to look like:

        from DLStudio import *
        
        convo_layers_config = "1x[128,3,3,1]-MaxPool(2) 1x[16,5,5,1]-MaxPool(2)"
        fc_layers_config = [-1,1024,10]
        
        dls = DLStudio(   dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
                          image_size = [32,32],
                          convo_layers_config = convo_layers_config,
                          fc_layers_config = fc_layers_config,
                          path_saved_model = "./saved_model",
                          momentum = 0.9,
                          learning_rate = 1e-3,
                          epochs = 2,
                          batch_size = 4,
                          classes = ('plane','car','bird','cat','deer',
                                     'dog','frog','horse','ship','truck'),
                          use_gpu = True,
                          debug_train = 0,
                          debug_test = 1,
                      )
        
        configs_for_all_convo_layers = dls.parse_config_string_for_convo_layers()
        convo_layers = dls.build_convo_layers2( configs_for_all_convo_layers )
        fc_layers = dls.build_fc_layers()
        model = dls.Net(convo_layers, fc_layers)
        dls.show_network_summary(model)
        dls.load_cifar_10_dataset()
        dls.run_code_for_training(model)
        dls.run_code_for_testing(model)
                

    or, if you would rather experiment with a drop-in network, your usage of the
    module is going to look something like:

        dls = DLStudio(   dataroot = "/home/kak/ImageDatasets/CIFAR-10/",
                          image_size = [32,32],
                          path_saved_model = "./saved_model",
                          momentum = 0.9,
                          learning_rate = 1e-3,
                          epochs = 2,
                          batch_size = 4,
                          classes = ('plane','car','bird','cat','deer',
                                     'dog','frog','horse','ship','truck'),
                          use_gpu = True,
                          debug_train = 0,
                          debug_test = 1,
                      )
        
        exp_seq = DLStudio.ExperimentsWithSequential( dl_studio = dls )   ## for your drop-in network
        exp_seq.load_cifar_10_dataset_with_augmentation()
        model = exp_seq.Net()
        dls.show_network_summary(model)
        exp_seq.run_code_for_training(model)
        exp_seq.run_code_for_testing(model)

        
    This assumes that you copy-and-pasted the network you want to
    experiment with in a class like ExperimentsWithSequential that is
    included in the module.


@tag_constructor
CONSTRUCTOR PARAMETERS: 

    batch_size:  Carries the usual meaning in the neural network context.

    classes:  A list of the symbolic names for the classes.

    convo_layers_config: This parameter allows you to specify a convolutional network
                  with a configuration string.  Must be formatted as explained in the
                  comment block associated with the method
                  "parse_config_string_for_convo_layers()"

    dataroot: This points to where your dataset is located.

    debug_test: Setting it allow you to see images being used and their predicted
                 class labels every 2000 batch-based iterations of testing.

    debug_train: Does the same thing during training that debug_test does during
                 testing.

    epochs: Specifies the number of epochs to be used for training the network.

    fc_layers_config: This parameter allows you to specify the final
                 fully-connected portion of the network with just a list of
                 the number of nodes in each layer of this portion.  The
                 first entry in this list must be the number '-1', which
                 stands for the fact that the number of nodes in the first
                 layer will be determined by the final activation volume of
                 the convolutional portion of the network.

    image_size:  The heightxwidth size of the images in your dataset.

    learning_rate:  Again carries the usual meaning.

    momentum:  Carries the usual meaning and needed by the optimizer.

    path_saved_model: The path to where you want the trained model to be
                  saved in your disk so that it can be retrieved later
                  for inference.

    use_gpu: You must set it to True if you want the GPU to be used for training.


@tag_methods
PUBLIC METHODS:

    (1)  build_convo_layers()

         This method creates the convolutional layers from the parameters in the
         configuration string that was supplied through the constructor option
         'convo_layers_config'.  The output produced by the call to
         'parse_config_string_for_convo_layers()' is supplied as the argument to
         build_convo_layers().

    (2)  build_fc_layers()

         From the list of ints supplied through the constructor option
         'fc_layers_config', this method constructs the fully-connected portion of
         the overall network.

    (3)  check_a_sampling_of_images()        

         Displays the first batch_size number of images in your dataset.


    (4)  display_tensor_as_image()

         This method will display any tensor of shape (3,H,W), (1,H,W), or just
         (H,W) as an image. If any further data normalizations is needed for
         constructing a displayable image, the method takes care of that.  It has
         two input parameters: one for the tensor you want displayed as an image
         and the other for a title for the image display.  The latter parameter is
         default initialized to an empty string.

    (5)  load_cifar_10_dataset()

         This is just a convenience method that calls on Torchvision's
         functionality for creating a data loader.

    (6)  load_cifar_10_dataset_with_augmentation()             

         This convenience method also creates a data loader but it also includes
         the syntax for data augmentation.

    (7)  parse_config_string_for_convo_layers()

         As mentioned in the Introduction, DLStudio allows you to specify a
         convolutional network with a string provided the string obeys the
         formatting convention described in the comment block of this method.
         This method is for parsing such a string. The string itself is presented
         to the module through the constructor option 'convo_layers_config'.

    (8)  run_code_for_testing()

         This is the method runs the trained model on the test data. Its output is
         a confusion matrix for the classes and the overall accuracy for each
         class.  The method has one input parameter which is set to the network to
         be tested.  This learnable parameters in the network are initialized with
         the disk-stored version of the trained model.

    (9)  run_code_for_training()

         This is the method that does all the training work. If a GPU was detected
         at the time an instance of the module was created, this method takes care
         of making the appropriate calls in order to transfer the tensors involved
         into the GPU memory.

    (10) save_model()

         Writes the model out to the disk at the location specified by the
         constructor option 'path_saved_model'.  Has one input parameter for the
         model that needs to be written out.

    (11) show_network_summary()

         Displays a print representation of your network and calls on the
         torchsummary module to print out the shape of the tensor at the output of
         each layer in the network. The method has one input parameter which is
         set to the network whose summary you want to see.


@tag_inner_classes
THE MAIN INNER CLASSES OF THE DLStudio CLASS:

    By "inner classes" I mean the classes that are defined within the class file
    DLStudio.py in the DLStudio directory of the distribution.  The DLStudio platform
    also includes several modules that reside at the same level of software
    abstraction as the main DLStudio class defined in the DLStudio.py file.

    The purpose of the following two inner classes is to demonstrate how you can
    create a custom class for your own network and test it within the framework
    provided by DLStudio.

    (1)  class ExperimentsWithSequential

         This class is my demonstration of experimenting with a network that I found
         on GitHub.  I copy-and-pasted it in this class to test its capabilities.
         How to call on such a custom class is shown by the following script in the
         Examples directory:

                     playing_with_sequential.py

    (2)  class ExperimentsWithCIFAR

         This is very similar to the previous inner class, but uses a common example
         of a network for experimenting with the CIFAR-10 dataset. Consisting of
         32x32 images, this is a great dataset for creating classroom demonstrations
         of convolutional networks.  As to how you should use this class is shown in
         the following script

                    playing_with_cifar10.py

         in the Examples directory of the distribution.

    (4)  class BMEnet (for connection skipping experiments)

         This class is for investigating the power of skip connections in deep
         networks.  Skip connections are used to mitigate a serious problem
         associated with deep networks --- the problem of vanishing gradients.  It
         has been argued theoretically and demonstrated empirically that as the depth
         of a neural network increases, the gradients of the loss become more and
         more muted for the early layers in the network.

    (5)  class DetectAndLocalize

         The code in this inner class is for demonstrating how the same convolutional
         network can simultaneously solve the twin problems of object detection and
         localization.  Note that, unlike the previous four inner classes, class
         DetectAndLocalize comes with its own implementations for the training and
         testing methods. The main reason for that is that the training for detection
         and localization must use two different loss functions simultaneously, one
         for classification of the objects and the other for regression. The function
         for testing is also a bit more involved since it must now compute two kinds
         of errors, the classification error and the regression error on the unseen
         data. Although you will find a couple of different choices for the training
         and testing functions for detection and localization inside
         DetectAndLocalize, the ones I have worked with the most are those that are
         used in the following two scripts in the Examples directory:

              run_code_for_training_with_CrossEntropy_and_MSE_Losses()

              run_code_for_testing_detection_and_localization()

    (6)  class CustomDataLoading

         This is a testbed for experimenting with a completely grounds-up attempt at
         designing a custom data loader.  Ordinarily, if the basic format of how the
         dataset is stored is similar to one of the datasets that Torchvision knows
         about, you can go ahead and use that for your own dataset.  At worst, you
         may need to carry out some light customizations depending on the number of
         classes involved, etc.  However, if the underlying dataset is stored in a
         manner that does not look like anything in Torchvision, you have no choice
         but to supply yourself all of the data loading infrastructure.  That is what
         this inner class of the DLStudio module is all about.

    (7)  class SemanticSegmentation

         This inner class is for working with the mUNet convolutional network for
         semantic segmentation of images.  This network allows you to segment out
         multiple objects simultaneously from an image.  Each object type is assigned
         a different channel in the output of the network.  So, for segmenting out
         the objects of a specified type in a given input image, all you have to do
         is examine the corresponding channel in the output.

    (8)  class Autoencoder

         The man reason for the existence of this class in DLStudio is for it to
         serve as the base class for VAE (Variational Auto-Encoder).  That way, the
         VAE class can focus exclusively on the random-sampling logic specific to
         variational encoding while the base class Autoencoder does the convolutional
         and transpose-convolutional heavy lifting associated with the usual
         encoding-decoding of image data.

    (9)  class VAE

         As mentioned above, VAE stands for "Variational Auto-Encoder". This class
         extends the base class Autoencoder with the variational logic for learning
         the latent distribution representation of a training dataset.  As to what
         that means, latent representations are based on the assumption that the
         "essence" of each sample of the input data can be represented by a vector in
         a lower-dimensional space that has a much simpler distribution (ideally an
         isotropic zero-mean and unit-covariance distribution) than what is possessed
         by the original training data samples.  Separating out the "essence" from
         the rest in the input images in this manner is referred to as
         "Disentanglement Learning."  One you have learned the latent distribution,
         you can sample it and embellish it in a Decoder to produce an output that is
         useful to the user.

    (10) class VQVAE

         VQVAE stands for "Vector Quantized Variational Auto Encoder", which is also
         frequently represented by the acronym VQ-VAE.  The concept of VQ-VAE was
         formulated in the 2018 paper "Neural Discrete Representation Learning" by
         van den Oord, Vinyals, and Kavukcuoglu. VQVAE is an important architecture
         in deep learning because it teaches us about what has come to be known as
         "Codebook Learning" for created discrete representations for images. The
         Codebook learned consists of a fixed number of embedding vectors.
         Subsequently, in an overall Encoder-Decoder architectures, you replace each
         pixel at the output of the Encoder with the closest embedding vector in the
         Codebook. The dimensionality you associate with a pixel at the output of the
         Encoder is the number of channels at that point.

    (11) class VQGAN

         VQGAN stands for "Vector Quantized Generative Adversarial Network".  There
         are two main differences between VQVAE and VQGAN: (1) The
         Encoder-VQ-Decoder" network in a VQGAN is trained through adversarial
         learning by encapsulating it in a GAN.  The concept of a GAN requires a
         Discriminator and a Generator, with the Discriminator trained to become an
         expert at recognizing the training images, while at the same time
         disbelieving the output of the Generator as looking like it came from the
         training set of images.  While you can use any run-of-the-mill discriminator
         in such adversarial learning, the Generator is nothing but our Encoder-VQ-
         Decoder network.  And (2) After training the VQGAN network, you train a
         transformer-based network for autoregressive modeling of the codebook
         indices as produced by the VectorQuantizer (VQ).  The codebook indices are
         the integer index values that point to the codebook vectors that are chosen
         as being the closest to the embedding vectors at the output of the Encoder.

    (12) class TextClassification

         The purpose of this inner class is to be able to use DLStudio for simple
         experiments in text classification.  Consider, for example, the problem of
         automatic classification of variable-length user feedback: you want to
         create a neural network that can label an uploaded product review of
         arbitrary length as positive or negative.  One way to solve this problem is
         with a Recurrent Neural Network in which you use a hidden state for
         characterizing a variable-length product review with a fixed-length state
         vector.

    (13) class TextClassificationWithEmbeddings

         This class has the same functionality as the previous text processing class
         except that now we use embeddings for representing the words.  Word
         embeddings are fixed-sized numerical vectors that are learned on the basis
         of the contextual similarity of the words. The implementation of this inner
         class uses the pre-trained 300-element word2vec embeddings as made available
         by Google for 3 million words and phrases drawn from the Google News
         dataset. In DLStudio, we access these embeddings through the popular gensim
         library.


@tag_coclasses
MODULES IN THE DLStudio PLATFORM:

    As stated at the beginning of the previous section, a module resides at the same
    level of software abstraction in the distribution directory as the main DLStudio
    class in the platform. Each module is defined in a separate subdirectory at the
    top level of the distribution directory.  While the main DLStudio class is
    defined in a subdirectory of the same name, the other subdirectories that contain
    the definitions for the modules are named AdversarialLearning, Seq2SeqLearning,
    DataPrediction, Transformers, GenerativeDiffusion, and MetricLearning.  What
    follows in this section are additional details regarding these co-classes:


@tag_coclass1
    ===============
    AdversarialLearning:
    ===============

    As I mentioned in the Introduction, the purpose of the AdversarialLearning class
    is to demonstrate probabilistic data modeling using Generative Adversarial
    Networks (GAN).  GANs use Discriminator-Generator or Critic-Generator pairs to
    learn probabilistic data models that can subsequently be used to create new image
    instances that look surprisingly similar to those in the training set.  At the
    moment, you will find the following three such pairs inside the
    AdversarialLearning class:

        1.  Discriminator-Generator DG1      ---  implements the DCGAN logic

        2.  Discriminator-Generator DG2      ---  a slight modification of the previous

        3.  Critic-Generator CG1                   ---  implements the Wasserstein GAN logic

        4.  Critic-Generator CG2                   ---  adds the Gradient Penalty to the 
                                                                      Wasserstein GAN logic.

    In the ExamplesAdversarialLearning directory of the distro you will see the
    following scripts that demonstrate adversarial learning as incorporated in the
    above networks:

        1.  dcgan_DG1.py                     ---  demonstrates the DCGAN DG1

        2.  dcgan_DG2.py                     ---  demonstrates the DCGAN DG2

        3.  wgan_CG1.py                      ---  demonstrates the Wasserstein GAN CG1

        4.  wgan_with_gp_CG2.py        ---  demonstrates the Wasserstein GAN CG2

    All of these scripts use the training dataset PurdueShapes5GAN that consists of
    20,000 images containing randomly shaped, randomly colored, and randomly
    positioned objects in 64x64 arrays.  The dataset comes in the form of a gzipped
    archive named "datasets_for_AdversarialLearning.tar.gz" that is provided under
    the link "Download the image dataset for AdversarialLearning" at the top of the
    HTML version of this doc page.  See the README in the ExamplesAdversarialLearning
    directory for how to unpack the archive.


@tag_coclass2
    ===============
    GenerativeDiffusion
    ===============

    During the last couple of years, Denoising Diffusion has emerged as a strong
    alternative to generative data modeling.  As mentioned previously in the
    Introduction section on this webpage, learning a data model through diffusion
    involves two Markov chains, one that incrementally diffuses a training image
    until it turns into pure noise, and the other that incrementally denoises pure
    noise until what you see is something like an image in your training dataset.
    The former is called the q-chain and the latter the p-chain.  The incremental
    diffusion in the q-chain is with known amount of Gaussian isotropic noise.  In
    the p-chain, on the other hand, the goal is for a neural network to learn from
    the diffusion carried out in the q-chain how to carry out a denoising operation
    that would amount to a reversal of that diffusion.

    All of the key elements of the code that I have presented in the
    GenerativeDiffusion module are extracted from OpenAI's "Improved Diffusion"
    project at GitHub that presents a PyTorch implementation of the work authored by
    Nichol and Dhariwal in their very famous paper "Improved Denoising Diffusion
    Probabilistic Models". See the beginning part of the doc page for the
    GenerativeDiffusion module for URLs to the GitHub code and their publication.

    If you want to play with the code in GenerativeDiffusion, your starting point
    should be the README in the ExamplesDiffusion directory of DLStudio distribution.
    The script RunCodeForDiffusion.py in that directory is what you will need to use
    to train the model for your own dataset.  As mentioned earlier, the goal of
    training is to make the neural network adept at estimating the p-chain transition
    probabilities p( x_{t-1} | x_t ) at all timesteps.  Once you have finished
    training, you would need to execute the script GenerateNewImageSamples.py for
    generating new images.


@tag_coclass3
    ===========
    Seq2SeqLearning:
    ===========

    As mentioned earlier in the Introduction, sequence-to-sequence learning (seq2seq)
    is about predicting an outcome sequence from a causation sequence, or, said
    another way, a target sequence from a source sequence.  Automatic machine
    translation is probably one of the most popular applications of seq2seq.
    DLStudio uses English-to-Spanish translation to illustrate the programming idioms
    and the PyTorch structures you would need for writing your own code for seq2seq.

    Any attempt at seq2seq for machine translation must answer the following question
    at the outset: How to represent the words of a language for neural-network based
    processing? In general, you have two options: (1) Have your overall network learn
    on its own what are known as vector embeddings for the words; or (2) Use
    pre-trained embeddings as provided by word2vec or Fasttext.

    After you have resolved the issue of word representation, your next challenge is
    how to implement the attention mechanism that you're going to need for aligning
    the similar grammatical units in the two languages. The seq2seq code demonstrated
    in this module uses the attention model proposed by Bahdanau, Cho, and Bengio in
    the form of a separate Attention class.  The name of this attention class is
    Attention_BCB.  In a separate attention class named Attention_SR, I have also
    included the attention mechanism used by Sean Robertson in his very popular NLP
    tutorial at the main PyTorch website.

    Seq2SeqLearning contains the following two inner classes for illustrating
    seq2seq:

        1.  Seq2SeqWithLearnableEmbeddings

        2.  Seq2SeqWithPretrainedEmbeddings

    In the first of these, Seq2SeqWithLearnableEmbeddings, the words embeddings are
    learned automatically by using the nn.Embeddings layer. On the other hand, in
    Seq2SeqWithPretrainedEmbeddings, I have used the word2vec embeddings for the
    source language English and allowed the system to learn the embeddings for the
    target language Spanish.

    In order to become familiar with these classes, your best entry points would be
    the following scripts in the ExamplesSeq2SeqLearning directory:

                seq2seq_with_learnable_embeddings.py

                seq2seq_with_pretrained_embeddings.py


@tag_coclass4
    ==========
    DataPrediction
    ==========

    As mentioned earlier in the Introduction, time-series data prediction differs
    from the more symbolic sequence-based learning frameworks with regard to the
    following: (1) Data normalization; (2) Data chunking; and (3) Datetime
    conditioning. The reason I mention data normalization is that now you have to
    remember the scaling parameters used for data normalization since you are going
    to need to inverse-normalize the predicted values. You would want to your
    predicted values to be at the same scale as the time-series observations.  The
    second issue, data chunking, refers to the fact that the notion of a "sentence"
    does not exist in time-series data.  What that implies that the user has to
    decide how to extract sequences from arbitrary long time-series data for training
    a prediction framework.  Finally, the the third issue, datetime conditioning,
    refers to creating a multi-dimensional encoding for the datetime stamp associated
    with each observation to account for the diurnal, weekly, seasonal, and other
    such temporal effects.

    The data prediction framework in the DataPrediction part of DLStudio is based on
    the following inner class:

        pmGRU

    for "Poor Man's GRU".  This GRU is my implementation of the "Minimal Gated Unit"
    GRU variant that was first presented by Joel Heck and Fathi Salem in their paper
    "Simplified Minimal Gated Unit Variations for Recurrent Neural Networks" and it
    combines the Update and the Reset gates of a regular GRU into a single gate
    called the Forget Gate.

    My reason for using pmGRU is purely educational. While you are likely to use
    PyTorch's GRU for any production work that requires a GRU, using a pre-programmed
    piece of code makes it more difficult to gain insights into how the logic of a
    GRU (especially with regard to the gating action it needs) is actually
    implemented.  The implementation code shown for pmGRU is supposed to help remedy
    that.

    As I mentioned in the Introduction, your main entry point for experimenting with
    data prediction is the following script in the ExamplesDataPrediction directory
    of the DLStudio distribution:

        power_load_prediction_with_pmGRU.py

    However, before you can run this script, you would need to download the training
    dataset used in this example.  See the "For Data Prediction" part of the "The
    Datasets Included" section of the doc page for that.


@tag_coclass5
    ========
    Transformers
    ========

    The code in this module of DLStudio consists of three different implementations
    of the transformer architecture: (1) TransformerFG, (2) TransformerPreLN, and (3)
    visTransformer.  The first two of these are meant for seq2seq learning, as in
    language translation, and the last is for solving the problem of image
    recognition.

    TransformerFG is my implementation of the architecture as conceptualized in the
    famous paper "Attention is All You Need" by Vaswani et el.  And TransformerPreLN
    is my implementation of the original idea along with the modifications suggested
    by Xiong et al. in their paper "On Layer Normalization in the Transformer
    Architecture" for more stable learning.  The two versions of transformers differ
    in only one respect: The placement of the LayerNorm in relation to the
    architectural components related to attention and the feedforward network.
    Literally, the difference is small, yet its consequences are significant
    regarding the stability of learning.  Finally, visTransformer is my
    implementation of the Vision Transformer as presented in the famous paper "An
    Image is Worth 16x16$ Words: Transformers for Image Recognition at Scale'' by
    Dosovitskiy et al.

    The fundamentals of how the attention works in all three transformer based
    implementations in the Transformers module are exactly the same.  For
    self-attention, you associate a Query Vector Q_i and a Key Vector K_i with each
    word w_i in a sentence.  For a given w_i, the dot product of its Q_i with the K_j
    vectors for all the other words w_j is a measure of how related w_i is to each
    w_j with regard to what's needed for the translation of a source sentence into
    the target sentence.  One more vector you associate with each word w_i is the
    Value Vector V_i.  The value vectors for the words in a sentence are weighted by
    the output of the activation nn.LogSoftmax applied to the dot-products.

    The self-attention mechanism described above is half of what goes into each base
    encoder of a transformer, the other half is a feedforward network (FFN). The
    overall encoder consists of a cascade of these base encoders.  In my
    implementation, I have referred to the overall encoder as the MasterEncoder.  The
    MasterDecoder also consists of a cascade of base decoders.  A base decoder is
    similar to a base encoder except for there being a layer of cross-attention
    interposed between the self-attention layer and the feedforward network.

    Referring to the attention half of each base encoder or a decoder as one
    half-unit and the FFN as the other half unit, the problem of vanishing gradients
    that would otherwise be caused by the depth of the overall network is mitigated
    by using LayerNorm and residual connections.  In TransformerFG, on the encoder
    side, LayerNorm is applied to the output of the self-attention layer and the
    residual connection wraps around both.  Along the same lines, LayerNorm is
    applied to the output of FFN and the residual connection wraps around both.

    In TransformerPreLN, on the other hand, LayerNorm is applied to the input to the
    self-attention layer and residual connection wraps around both.  Similarly,
    LayerNorm is applied to the input to FFN and the residual connection wraps around
    both.  Similar considerations applied to the decoder side, except we now also
    have a layer of cross-attention interposed between the self-attention and FFN.
   
    As I mentioned in the Introduction, your main entry point for experimenting with
    the seq2seq based transformer code in DLStudio are the following two scripts in
    the ExamplesTransformers directory of the distribution:

        seq2seq_with_transformerFG.py
        seq2seq_with_transformerPreLN.py

    However, before you can run these scripts, you would need to download the
    training dataset used in these examples.  See the "For Transformers" part of the
    "The Datasets Included" section of this doc page for that.

    And your main entry point for experimenting with image recognition by playing
    with the visTransformer class are the scripts:

          image_recog_with_visTransformer.py
          test_checkpoint_for_visTransformer.py 

    Both these script use the CIFAR10 dataset for demonstrating image recognition.


@tag_coclass6
    =============
    MetricLearning:
    =============

    As mentioned in the Introduction, the main idea of metric learning is to learn a
    mapping from the images to their embedding vector representations in such a way
    that the embeddings for what are supposed to be similar images are pulled
    together and those for dissimilar images are pulled as far apart as possible.
    Two loss functions are commonly used for this type of deep learning: Pairwise
    Contrastive Loss and Triplet Loss.

    To calculate the Pairwise Contrastive Loss, you must first extract Positive and
    Negative Pairs from a batch.  A Positive Pair means that both the embeddings in
    the pair carry the same class label and a Negative Pair means that the two
    embeddings in the pair have dissimilar labels.

    From a programming standpoint, the challenge is how to form these pairs without
    scanning through a batch with 'for' loops --- since such loops are an anathema to
    any GPU based processing of data. What comes to our rescue are a combination of
    the broadcast properties of tensors (inherited from numpy) and tensor-based
    Boolean logic. For example, by comparing a column tensor of the sample labels in
    a batch with a row tensor of the same and testing for the equality of the sample
    labels, you instantly have a 2D array whose (i,j) element is True if the i-th and
    the j-th batch samples carry the same class label.

    Even after you have constructed the Positive and the Negative Pairs from a batch,
    your next mini-challenge is to reformat the batch sample indices in the pairs in
    order to conform to the input requirements of PyTorch's loss function
    torch.nn.CosineEmbeddingLoss.  The input consists of three tensors, the first two
    of which are of shape (N,M), where N is the total number of pairs extracted from
    the batch and M the size of the embedding vectors. The first such NxM tensor
    corresponds to the fist batch sample index in each pair. And the second such NxM
    tensor corresponds to the second batch sample index in each pair. The last tensor
    in the input args to the CosineEmbeddingLoss loss function is of shape Nx1, in
    which the individual values are either +1.0 or -1.0, depending on whether the
    pair formed by the first two embeddings is a Positive Pair or a Negative Pair.

    For the Triplet Loss, you construct triplets of the samples in a batch in which
    the first two embeddings must carry the same class label and the label of the
    third embedding must not be same as for the other two.  Such a triplet is
    commonly denoted (Anchor, Pos, Neg).  That is, you treat the first element as the
    Anchor, the second as the Positive and the third as the Negative.  A triplet is
    formed only if the distance between the Anchor and the Neg is greater than the
    distance between the Anchor and the Pos.  We want all such Neg element to get
    farther away from the Anchor compared to how far the Pos element is --- but no
    farther than what's known as the Margin.  The idea is that if the Neg element is
    already beyond the Margin distance added to how far the Pos is, the Neg is
    already well separated from Pos and would not contribute to the learning process.

    The programming challenge for calculating the Triplet Loss is similar to what it
    is for the Pairwise Contrastive Loss: How to extract all the triplets from a
    batch without using 'for' loops.  The first step is to form array index triplets
    (i,j,k) in which two indices are the same.  If B is the batch size, this is
    easily done by first forming a BxB array that is the logical negation of a
    Boolean array of the same size whose True values are only on the diagonal.  We
    can reshape this BxB Boolean array into three BxBxB shaped Boolean arrays, the
    first in which the True values exist only where i and j values are not the same,
    the second in which the True values occur only when i and k index values are not
    the same, and the third that has True values only when the j and k index values
    are not the same.  By taking a logical AND of all three BxBxB Boolean arrays, we
    get the result we want.  Next, we construct a BxBxB Boolean tensor in which the
    True values occur only where the first two index values imply that their
    corresponding labels are identical and where the last index corresponds to a
    label that does not agree with that for the first two index values.

    Even after you have formed the triplets, your next mini-challenge is to reformat
    the triplets into what you need to feed into the PyTorch loss function
    torch.nn.TripletMarginLoss. The loss function takes three arguments, each of
    shape (N,M) where N is the total number of triplets extracted from the batch and
    M the size of the embedding vectors.  The first such NxM tensor is the Anchor
    embedding vectors, the second for the Positive embedding vectors, the last for
    the Negative embedding vectors.

    If you wish to use this module to learn about metric learning, your entry points
    should be the following scripts in the ExamplesMetricLearning directory of the
    distro:

        1.  example_for_pairwise_contrastive_loss.py

        2.  example_for_triplet_loss.py

    As the names imply, the first script demonstrates using the Pairwise Contrastive
    Loss for metric learning and the second script using the Triplet Loss for doing
    the same.  Both scripts can work with either the pre-trained ResNet-50 trunk
    model or the homebrewed network supplied with the MetricLearning module.


@tag_examples_dir
Examples DIRECTORY:

    The Examples subdirectory in the distribution contains the following scripts:

    (1)  playing_with_reconfig.py

         Shows how you can specify a convolution network with a configuration string.
         The main DLStudio class parses the string constructs the network.

    (2)  playing_with_sequential.py

         Shows you how you can call on a custom inner class of the 'DLStudio' module
         that is meant to experiment with your own network.  The name of the inner
         class in this example script is ExperimentsWithSequential

    (3)  playing_with_cifar10.py

         This is very similar to the previous example script but is based on the
         inner class ExperimentsWithCIFAR which uses more common examples of networks
         for playing with the CIFAR-10 dataset.

    (5)  playing_with_skip_connections.py

         This script illustrates how to use the inner class BMEnet of the module for
         experimenting with skip connections in a CNN. As the script shows, the
         constructor of the BMEnet class comes with two options: skip_connections and
         depth.  By turning the first on and off, you can directly illustrate in a
         classroom setting the improvement you can get with skip connections.  And by
         giving an appropriate value to the "depth" option, you can show results for
         networks of different depths.

    (6)  custom_data_loading.py

         This script shows how to use the custom dataloader in the inner class
         CustomDataLoading of the main DLStudio class.  That custom dataloader is
         meant specifically for the PurdueShapes5 dataset that is used in object
         detection and localization experiments in DLStudio.

    (7)  object_detection_and_localization.py

         This script shows how you can use the functionality provided by the inner
         class DetectAndLocalize of the main DLStudio class for experimenting with
         object detection and localization.  Detecting and localizing (D&L) objects
         in images is a more difficult problem than just classifying the objects.
         D&L requires that your CNN make two different types of inferences
         simultaneously, one for classification and the other for localization.  For
         the localization part, the CNN must carry out what is known as
         regression. What that means is that the CNN must output the numerical values
         for the bounding box that encloses the object that was detected.  Generating
         these two types of inferences requires two DIFFERENT loss functions, one for
         classification and the other for regression.

    (8)  noisy_object_detection_and_localization.py

         This script in the Examples directory is exactly the same as the one
         described above, the only difference is that it calls on the noise-corrupted
         training and testing dataset files.  I thought it would be best to create a
         separate script for studying the effects of noise, just to allow for the
         possibility that the noise-related studies with DLStudio may evolve
         differently in the future.

    (9)  object_detection_and_localization_iou.py

         This script in the Examples directory is for experimenting with the variants
         of the IoU (Intersection over Union) loss functions provided by the class
         DIoULoss class that is a part of DLStudio's inner class DetectAndLocalize.
         This script uses the same datasets as the script mentioned in item 7 above.

    (10) semantic_segmentation.py

         This script should be your starting point if you wish to learn how to use
         the mUNet neural network for semantic segmentation of images.  As mentioned
         elsewhere in this documentation page, mUNet assigns an output channel to
         each different type of object that you wish to segment out from an
         image. So, given a test image at the input to the network, all you have to
         do is to examine each channel at the output for segmenting out the objects
         that correspond to that output channel.

    (11) run_autoencoder.py

         Even though the main purpose of the Autoencoder class in DLStudio is to
         serve as the Base class for the VAE class, this script allows you to
         experiment with just the Autoencoder class by itself.  For example, if you
         wanted to experiment with dimensionality reduction with an Autoencoder, all
         you would need to do would be to change the last or the last couple of
         layers of the Decoder in the Autoencoder class and see for yourself the
         results by running this script.
         

    (12) run_vae.py

         You can use this script to experiment with the variational autoencoding code
         in the VAE (Variational Auto-Encoder) inner class of DLStudio.  Variational
         autoencoding means mapping an input image to a latent vector that captures
         the "essence" of what's in the image with the assumption that the latent
         vectors form a much distribution (ideally a zero-mean, unit covariance
         Gaussian) than the original input data.  The Decoder part of a VAE samples
         the latent distribution and can be trained to create useful variants of the
         input data.

    (13) run_vae_for_image_generation.py

         This script allows you to experiment with just the Decoder part of the VAE
         (Variational Auto-Encoder) class.  The VAE Decoder is in reality a Generator
         samples a Gaussian probability distribution, as specified by its mean and
         covariance, and transforms the sample thus created into an output image that
         will bear some resemblance with the training images.  As to how close the
         output image will come to looking like your images in the training dataset
         would depend on the size of the dataset, the complexity of the images, the
         dimensionality of the latent space (this dimensionality is 8192) for the VAE
         network as implemented in DLStudio), etc.

    (14) run_vqvae.py

         Run this script to experiment with the VQVAE inner class in the main
         DLStudio class. VQVAE is about what has come to he known as Codebook
         learning for more efficient discrete representation of images with a finite
         vocabulary of embedding vectors.

    (15) run_vqgan.py

         While the overall goal in this script is the same as in the previous script
         --- Codebook learning --- this script does a couple of fancier things.
         First, it encapsulates the Encoder-VQ-Decoder network in a GAN and trains
         the network in an adversarial fashion.  The basic VQGAN network trained in
         this fashion is then used in the next script for transformer-based
         autoregressive modeling of the Codebook indices to which each input image is
         mapped.

    (16) run_vqgan_transformer.py

         This script is paired with the previous script.  That is, you must first run
         the previous script and train well the basic Encoder-VQ-Decoder network of a
         VQGAN.  Only after that, you can run this script for autoregressive modeling
         of the images based on representing the images in the Latest Space with
         sequences of integer indices, with each integer index representing a
         codebook vector.
      
    (17) run_vqgan_map_image_to_codebook.py

         This script is also meant to be run after you have already trained the basic
         VQGAN network with the script run_vqgan.py.  The goal of this script is to
         make it easy for you play with individual images or a batch of images to see
         the mappings between the images and the codebook vectors. See the commented
         out block at the top of this file to appreciate the reasons for why you
         might want to play with this script

    (18) text_classification_with_TEXTnet.py

         This script is your first introduction in DLStudio to a Recurrent Neural
         Network, meaning a neural-network with feedback.  Such networks are needed
         for solving problems related to variable length input data in applications
         such as text classification, sentiment analysis, machine translation, etc.
         Unfortunately, unless care is taken, the feedback in such networks results
         in long chains of dependencies and thus exacerbates the vanishing gradients
         problem.  The specific goal of this script is neural learning for automatic
         classification of product reviews.

    (19) text_classification_with_TEXTnet_word2vec.py

         This script uses the same learning network as in the previous script, but
         there is a big difference between the two.  The previous network uses
         one-hot vectors for representing the words. On the other hand, this script
         uses pre-trained word2vec embeddings.  These are fixed-sized numerical
         vectors that are learned on the basis of contextual similarities.
        
    (20) text_classification_with_TEXTnetOrder2.py

         As mentioned earlier for the script in item 10 above, the vanishing
         gradients problem becomes worse in neural networks with feedback.  One way
         to get around this problem is to use what's known as "gated recurrence".
         This script uses the TEXTnetOrder2 network as a stepping stone to a
         full-blown implementation of gating as provided by the nn.GRU class in item
         14 below.

    (21) text_classification_with_TEXTnetOrder2_word2vec.py

         This script uses the same network as the previous script, but now we use the
         word2vec embeddings for representing the words.

    (22) text_classification_with_GRU.py

         This script demonstrates how one can use a GRU (Gated Recurrent Unit) to
         remediate one of the main problems associated with recurrence -- vanishing
         gradients in the long chains of dependencies created by feedback.

    (23) text_classification_with_GRU_word2vec.py

         While this script uses the same learning network as the previous one, the
         words are now represented by fixed-sized word2vec embeddings.



@tag_examples_advers_dir
ExamplesAdversarialLearning DIRECTORY:

    The ExamplesAdversarialLearning directory of the distribution contains the
    following scripts for demonstrating adversarial learning for data modeling:

        1.  dcgan_DG1.py            

        2.  dcgan_DG2.py   

        3.  wgan_CG1.py             

        4.  wgan_with_gp_CG2.py

    The first script demonstrates the DCGAN logic on the PurdueShapes5GAN dataset.
    In order to show the sensitivity of the basic DCGAN logic to any variations in
    the network or the weight initializations, the second script introduces a small
    change in the network.  The third script is a demonstration of using the
    Wasserstein distance for data modeling through adversarial learning.  The fourth
    script adds a Gradient Penalty term to the Wasserstein Distance based logic of
    the third script.  The PurdueShapes5GAN dataset consists of 64x64 images with
    randomly shaped, randomly positioned, and randomly colored shapes.

    The results produced by these scripts (for the constructor options shown in the
    scripts) are included in a subdirectory named RVLCloud_based_results.  If you are
    just becoming familiar with the AdversarialLearning class of DLStudio, I'd urge
    you to run the script with the constructor options as shown and to compare your
    results with those that are in the RVLCloud_based_results directory.



@tag_examples_diffusion_dir
ExamplesDiffusion DIRECTORY:

    The ExamplesDiffusion directory of DLStudio contains the following files that you
    will find helpful for your experiments with diffusion:

       0.  README

       1.  RunCodeForDiffusion.py

       2.  GenerateNewImageSamples.py

       3.  VisualizeSamples.py

    Any experiment with diffusion will involve all three scripts mentioned above.
    The script RunCodeForDiffusion.py is for training the neural network to become
    adept at learning the p-chain transition probabilities p( x_{t-1} | x_t ).  The
    script GenerateNewImageSamples.py is for generating the images using the learned
    model.  This script deposits all the generated images in a numpy archive for
    ndarrays.  The last script, VisualizeSamples.py, is for extracting the individual
    images from that archive.  Please make sure that you have gone through the README
    mentioned above before starting your experiments with the diffusion part of
    DLStudio.


@tag_examples_seq2seq_dir
ExamplesSeq2SeqLearning DIRECTORY:

    The ExamplesSeq2SeqLearning directory of the distribution contains the following
    scripts for demonstrating sequence-to-sequence learning:

    (1) seq2seq_with_learnable_embeddings.py

         This script demonstrates the basic PyTorch structures and idioms to use for
         seq2seq learning.  The application example addressed in the script is
         English-to-Spanish translation.  And the attention mechanism used for
         seq2seq is the one proposed by Bahdanau, Cho, and Bengio.  This network used
         in this example calls on the nn.Embeddings layer in the encoder to learn the
         embeddings for the words in the source language and a similar layer in the
         decoder to learn the embeddings to use for the target language.

    (2) seq2seq_with_pretrained_embeddings.py

         This script, also for seq2seq learning, differs from the previous one in
         only one respect: it uses Google's word2vec embeddings for representing the
         words in the source-language sentences (English).  As to why I have not used
         at this time the pre-trained embeddings for the target language is explained
         in the main comment doc associated with the class
         Seq2SeqWithPretrainedEmbeddings.


@tag_examples_predict
ExamplesDataPrediction DIRECTORY:

    The ExamplesDataPrediction directory of the distribution contains the following
    script for demonstrating data prediction for time-series data:

        power_load_prediction_with_pmGRU.py

    This script uses a subset of the dataset provided by Kaggle for one of their
    machine learning competitions.  The dataset consists of over 10-years worth of
    hourly electric load recordings made available by several utilities in the east
    and the Midwest of the United States.  You can download this dataset from a link
    at the top of the main DLStudio doc page.


@tag_examples_xform
ExamplesTransformers DIRECTORY:

    The ExamplesTransformers directory of the distribution contains the following
    four scripts for experimenting with transformers in DLStudio:

        seq2seq_with_transformerFG.py 
        seq2seq_with_transformerPreLN.py         

        image_recog_with_visTransformer.py
        test_checkpoint_for_visTransformer.py 


    The first two scripts deal with English-to-Spanish translation in a manner
    similar to what's demonstrated by the code in the Seq2SeqLearning module and the
    example scripts associated with that module. The last two relate to my
    demonstration of image recognition with a transformer based implementation.  I
    have used the CFAR10 dataset for image recognition.


@tag_examples_metric
ExamplesMetricLearning DIRECTORY:

    The ExamplesMetricLearning directory at top level of the distribution contains
    the following scripts:

        1.  example_for_pairwise_contrastive_loss.py

        2.  example_for_triplet_loss.py

    As the names imply, the first script demonstrates using the Pairwise Contrastive
    Loss for metric learning and the second script using the Triplet Loss for doing
    the same.  Both scripts can work with either the pre-trained ResNet-50 trunk
    model or the homebrewed network supplied with the MetricLearning module.


@tag_datasets
THE DATASETS INCLUDED: 

    [must be downloaded separately]

@tag2_main_dlstudio
    FOR THE MAIN DLStudio CLASS and its INNER CLASSES:

        Download the dataset archive 'datasets_for_DLStudio.tar.gz' through the link
        "Download the image datasets for the main DLStudio Class" provided at the top
        of this documentation page and store it in the 'Example' directory of the
        distribution.  Subsequently, execute the following command in the 'Examples'
        directory:
    
            cd Examples
            tar zxvf datasets_for_DLStudio.tar.gz
    
        This command will create a 'data' subdirectory in the 'Examples' directory
        and deposit the datasets mentioned below in that subdirectory.
    
@tag3_dataset
        FOR OBJECT DETECTION AND LOCALIZATION:
    
        Training a CNN for object detection and localization requires training and
        testing datasets that come with bounding-box annotations. This module comes
        with the PurdueShapes5 dataset for that purpose.  I created this
        small-image-format dataset out of my admiration for the CIFAR-10 dataset as
        an educational tool for demonstrating classification networks in a classroom
        setting. You will find the following dataset archive files in the "data"
        subdirectory of the "Examples" directory of the distro:
    
            (1)  PurdueShapes5-10000-train.gz
                 PurdueShapes5-1000-test.gz
    
            (2)  PurdueShapes5-20-train.gz
                 PurdueShapes5-20-test.gz               
    
        The number that follows the main name string "PurdueShapes5-" is for the
        number of images in the dataset.  You will find the last two datasets, with
        20 images each, useful for debugging your logic for object detection and
        bounding-box regression.
    
        As to how the image data is stored in the archives, please see the main
        comment block for the inner class CustomLoading in this file.
    
@tag3_dataset
        FOR DETECTING OBJECTS IN NOISE-CORRUPTED IMAGES:
    
        In terms of how the image data is stored in the dataset files, this dataset
        is no different from the PurdueShapes5 dataset described above.  The only
        difference is that we now add varying degrees of noise to the images to make
        it more challenging for both classification and regression.
    
        The archive files you will find in the 'data' subdirectory of the 'Examples'
        directory for this dataset are:
    
            (3)  PurdueShapes5-10000-train-noise-20.gz
                 PurdueShapes5-1000-test-noise-20.gz
    
            (4)  PurdueShapes5-10000-train-noise-50.gz
                 PurdueShapes5-1000-test-noise-50.gz
    
            (5)  PurdueShapes5-10000-train-noise-80.gz
                 PurdueShapes5-1000-test-noise-80.gz
    
        In the names of these six archive files, the numbers 20, 50, and 80 stand for
        the level of noise in the images.  For example, 20 means 20% noise.  The
        percentage level indicates the fraction of the color value range that is
        added as randomly generated noise to the images.  The first integer in the
        name of each archive carries the same meaning as mentioned above for the
        regular PurdueShapes5 dataset: It stands for the number of images in the
        dataset.
    
@tag3_dataset
        FOR SEMANTIC SEGMENTATION:
    
        Showing interesting results with semantic segmentation requires images that
        contains multiple objects of different types.  A good semantic segmenter
        would then allow for each object type to be segmented out separately from an
        image.  A network that can carry out such segmentation needs training and
        testing datasets in which the images come up with multiple objects of
        different types in them. Towards that end, I have created the following
        dataset:

            (6) PurdueShapes5MultiObject-10000-train.gz
                PurdueShapes5MultiObject-1000-test.gz
    
            (7) PurdueShapes5MultiObject-20-train.gz
                PurdueShapes5MultiObject-20-test.gz
    
        The number that follows the main name string "PurdueShapes5MultiObject-" is
        for the number of images in the dataset.  You will find the last two
        datasets, with 20 images each, useful for debugging your logic for semantic
        segmentation.
    
        As to how the image data is stored in the archive files listed above, please
        see the main comment block for the class
    
            PurdueShapes5MultiObjectDataset
    
        As explained there, in addition to the RGB values at the pixels that are
        stored in the form of three separate lists called R, G, and B, the shapes
        themselves are stored in the form an array of masks, each of size 64x64, with
        each mask array representing a particular shape. For illustration, the
        rectangle shape is represented by the first such array. And so on.
    
@tag3_dataset
        FOR TEXT CLASSIFICATION:
    
        My experiments tell me that, when using gated RNNs, the size of the
        vocabulary can significantly impact the time it takes to train a neural
        network for text modeling and classification.  My goal was to provide curated
        datasets extract from the Amazon user-feedback archive that would lend
        themselves to experimentation on, say, your personal laptop with a
        rudimentary GPU like the Quadro.  Here are the new datasets you can now
        download from the main documentation page for this module:
        
    
                 sentiment_dataset_train_200.tar.gz        vocab_size = 43,285
                 sentiment_dataset_test_200.tar.gz  
    
                 sentiment_dataset_train_40.tar.gz         vocab_size = 17,001
                 sentiment_dataset_test_40.tar.gz    
    
                 sentiment_dataset_train_400.tar.gz        vocab_size = 64,350
                 sentiment_dataset_test_400.tar.gz  
    
        As with the other datasets, the integer in the name of each dataset is the
        number of reviews collected from the 'positive.reviews' and the
        'negative.reviews' files for each product category.  Therefore, the dataset
        with 200 in its name has a total of 400 reviews for each product category.
        Also provided are two datasets named "sentiment_dataset_train_3.tar.gz" and
        sentiment_dataset_test_3.tar.gz" just for the purpose of debugging your code.
    
        The last dataset, the one with 400 in its name, was added in Version 1.1.3 of
        the module.

@tag2_dataset
    FOR Seq2Seq LEARNING:

        For sequence-to-sequence learning with DLStudio, you can download an
        English-Spanish translation corpus through the following archive:

            en_es_corpus_for_seq2sq_learning_with_DLStudio.tar.gz

        This data archive is a lightly curated version of the main dataset posted at
        "http://www.manythings.org/anki/" by the folks at "tatoeba.org".  My
        alterations to the original dataset consist mainly of expanding the
        contractions like "it's", "I'm", "don't", "didn't", "you'll", etc., into
        their "it is", "i am", "do not", "did not", "you will", etc. The original
        form of the dataset contains 417 such unique contractions.  Another
        alteration I made to the original data archive is to surround each sentence
        in both English and Spanish by the "SOS" and "EOS" tokens, with the former
        standing for "Start of Sentence" and the latter for "End of Sentence".

        Download the above archive in the ExamplesSeq2Seq2Learning directory and
        execute the following command in that directory:

            tar zxvf en_es_corpus_for_seq2sq_learning_with_DLStudio.tar.gz
    
        This command will create a 'data' subdirectory in the directory
        ExamplesSeq2Seq2Learning and deposit the following dataset archive in that
        subdirectory:

            en_es_8_98988.tar.gz

        Now execute the following in the 'data' directory:

            tar zxvf en_es_8_98988.tar.gz

        With that, you should be able to execute the Seq2SeqLearning based scripts in
        the 'ExamplesSeq2SeqLearning' directory.


@tag2_dataset
    FOR ADVERSARIAL LEARNING AND DIFFUSION:

        Download the dataset archive

            datasets_for_AdversarialLearning.tar.gz 

        through the link "Download the image dataset for AdversarialLearning"
        provided at the top of the HTML version of this doc page and store it in the
        'ExamplesAdversarialLearning' directory of the distribution.  Subsequently,
        execute the following command in the directory 'ExamplesAdversarialLearning':
    
            tar zxvf datasets_for_AdversarialLearning.tar.gz
    
        This command will create a 'dataGAN' subdirectory and deposit the following
        dataset archive in that subdirectory:

            PurdueShapes5GAN-20000.tar.gz

        Now execute the following in the "dataGAN" directory:

            tar zxvf PurdueShapes5GAN-20000.tar.gz

        With that, you should be able to execute the adversarial learning based
        scripts in the 'ExamplesAdversarialLearning' directory.

        NOTE ADDED IN VERSION 2.5.1: This dataset is also used for the three scripts
        related to autoencoding and variational autoencoding in the Examples
        directory of the distribution.


@tag2_dataset
    FOR DATA PREDICTION:

        Download the dataset archive     

            dataset_for_DataPrediction.tar.gz             

        into the ExamplesDataPrediction directory of the DLStudio distribution.
        Next, execute the following command in that directory:

            tar zxvf dataset_for_DataPrediction.tar.gz 

        That will create data directory named "dataPred" in the
        ExamplesDataPrediction directory.  With that you should be able to execute
        the data prediction script in that directory.


@tag2_dataset
    FOR TRANSFORMERS:

        For the seq2seq learning part of the Transformers module in DLStudio,
        download the dataset archive

            en_es_corpus_for_learning_with_Transformers.tar.gz

        into the ExamplesTransformers directory of the DLStudio distribution.  Next,
        execute the following command in that directory:

            tar zxvf en_es_corpus_for_learning_with_Transformers.tar.gz

        That will create a 'data' subdirectory in the ExamplesTransformers directory
        and deposit in that subdirectory the following archives

            en_es_xformer_8_10000.tar.gz
            en_es_xformer_8_90000.tar.gz

        These are both derived from the same data source as in the dataset for the
        examples associated with the Seq2SeqLearning module.  The first has only
        10,000 pars of English-Spanish sentences and meant primarily for debugging
        purposes.  The second contains 90000 pairs of such sentences.  The number '8'
        in the dataset names means that no sentence contains more than 8 real words.
        With the "SOS" and "EOS" tokens used as sentence delimiters, the maximum
        number of words in each sentence in either language is 10.


@tag_bugs
BUGS:

    Please notify the author if you encounter any bugs.  When sending email, please
    place the string 'DLStudio' in the subject line to get past the author's spam
    filter.


@tag_ack
ACKNOWLEDGMENTS:

    Thanks to Praneet Singh and Noureldin Hendy for their comments related to the
    buggy behavior of the module when using the 'depth' parameter to change the size
    of a network. Thanks also go to Christina Eberhardt for reminding me that I
    needed to change the value of the 'dataroot' parameter in my Examples scripts
    prior to packaging a new distribution.  Their feedback led to Version 1.1.1 of
    this module.  Regarding the changes made in Version 1.1.4, one of them is a fix
    for the bug found by Serdar Ozguc in Version 1.1.3. Thanks Serdar.

    Version 2.0.3: I owe thanks to Ankit Manerikar for many wonderful conversations
    related to the rapidly evolving area of generative adversarial networks in deep
    learning.  It is obviously important to read research papers to become familiar
    with the goings-on in an area.  However, if you wish to also develop deep
    intuitions in those concepts, nothing can beat having great conversations with a
    strong researcher like Ankit.  Ankit is finishing his Ph.D. in the Robot Vision
    Lab at Purdue.

    Version 2.2.2: My laboratory's (RVL) journey into the world of transformers began
    with a series of lab seminars by Constantine Roros and Rahul Deshmukh.  Several
    subsequent conversations with them were instrumental in helping me improve the
    understanding I had gained from the seminars.  Additional conversations with
    Rahul about the issue of masking were important to how I eventually implemented
    those ideas in my code.

    Rahul Deshmukh discovered the reason as to why my implementation of the skip
    connection code was not working with the more recent versions of PyTorch.  My
    problem was using in-place operations in the forward() of the networks that
    called for connection skipping. This led to the release of Version 2.3.3 of
    DLStudio.

    The main reason for Version 2.3.4 was my new design for the SkipBlock class and
    also my easier-to-understand code for the BMEnet class that showcases the
    importance of providing shortcut paths in a computational graph using skip
    blocks.  After I broadcast that code to the students in my DL class at Purdue,
    Cheng-Hao Chen reported that when a SkipBlock was asked to change the channels
    from its input to its output but without downsampling the input, that elicited an
    error from the system.  Cheng-Hao also provided a correction for the error.
    Thanks, Cheng-Hao!

    Aditya Chauhan proved to be a great sounding board in my journey into the land of
    diffusion that led to Version 2.4.2.  I particularly appreciated Aditya's help in
    understanding how the attention mechanism worked in the OpenAI code library at
    GitHub.  Aditya is working for his PhD in RVL.  Thanks, Aditya!

    Version 2.5.0 is a result of Rahul Deshmukh insisting that the number of
    learnable parameters in a transformer must not depend on the maximum expected
    length for the input sequence --- which was not the case with the previous
    versions of the transformer code in DLStudio. As it turned out, my implementation
    of the FFN layer in the basic transformer encoder/decoder blocks was not in
    keeping with the design laid out in the original paper by Vaswani et al.  This
    problem is now fixed in Version 2.5.0. Rahul is at the very end of his Ph.D
    program in RVL at Purdue.  Thanks, Rahul!

    The main reason for Version 2.5.3 is Aditya Chauhan's strongly held opinion that
    the nn.Softmax normalization of the "Q.K^T" dot-products for Attention
    calculations must be along the word-axis for the K-tensors and NOT along the
    word-axis for the Q-tensors. His reasoning is compelling because, with the
    normalization along the K-axis, the individual rows of the normalized dot-product
    possess a more natural probability based interpretation: For each word in the
    Query tensor, the numbers in the corresponding row in the normalized dot product
    are the probabilities of the other words being relevant to the query word.  I
    wish to thank Aditya for sharing his insights with me.


@tag_about_the_author
ABOUT THE AUTHOR:

    The author, Avinash Kak, is a professor of Electrical and Computer Engineering
    at Purdue University.  For all issues related to this module, contact the
    author at kak@purdue.edu. If you send email, please place the string
    "DLStudio" in your subject line to get past the author's spam filter.


@tag_copyright
COPYRIGHT:

    Python Software Foundation License

    Copyright 2025 Avinash Kak

@endofdocs
'''


import sys,os,os.path,glob
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision                  
import torchvision.transforms as tvt
import torch.optim as optim
import numpy as np
from PIL import ImageFilter
from PIL import Image
import numbers
import re
import math
import random
import copy
import matplotlib.pyplot as plt
import gzip
import pickle
import pymsgbox
import time
import logging

import torchmetrics                                                             ##  for VQGAN
from torchmetrics.image.lpip import LearnedPerceptualImagePatchSimilarity       ##  for VQGAN


## Python does not have a decorator for declaring static vars.  But you can use
## the following for achieving the same effect.  I believe I saw it at stackoverflow.com:
def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

#______________________________  DLStudio Class Definition  ________________________________

class DLStudio(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''DLStudio constructor can only be called with keyword arguments for 
                      the following keywords: epochs, learning_rate, batch_size, momentum,
                      convo_layers_config, image_size, dataroot, path_saved_model, classes, 
                      image_size, convo_layers_config, fc_layers_config, debug_train, use_gpu, and 
                      debug_test''')
        learning_rate = epochs = batch_size = convo_layers_config = momentum = None
        image_size = fc_layers_config = dataroot =  path_saved_model = classes = use_gpu = None
        debug_train  = debug_test = None
        if 'dataroot' in kwargs                      :   dataroot = kwargs.pop('dataroot')
        if 'learning_rate' in kwargs                 :   learning_rate = kwargs.pop('learning_rate')
        if 'momentum' in kwargs                      :   momentum = kwargs.pop('momentum')
        if 'epochs' in kwargs                        :   epochs = kwargs.pop('epochs')
        if 'batch_size' in kwargs                    :   batch_size = kwargs.pop('batch_size')
        if 'convo_layers_config' in kwargs           :   convo_layers_config = kwargs.pop('convo_layers_config')
        if 'image_size' in kwargs                    :   image_size = kwargs.pop('image_size')
        if 'fc_layers_config' in kwargs              :   fc_layers_config = kwargs.pop('fc_layers_config')
        if 'path_saved_model' in kwargs              :   path_saved_model = kwargs.pop('path_saved_model')
        if 'classes' in kwargs                       :   classes = kwargs.pop('classes') 
        if 'use_gpu' in kwargs                       :   use_gpu = kwargs.pop('use_gpu') 
        if 'debug_train' in kwargs                   :   debug_train = kwargs.pop('debug_train') 
        if 'debug_test' in kwargs                    :   debug_test = kwargs.pop('debug_test') 
        if len(kwargs) != 0: raise ValueError('''You have provided unrecognizable keyword args''')
        if dataroot:
            self.dataroot = dataroot
        if convo_layers_config:
            self.convo_layers_config = convo_layers_config
        if image_size:
            self.image_size = image_size
        if fc_layers_config:
            self.fc_layers_config = fc_layers_config
            if fc_layers_config[0] != -1:
                raise Exception("""\n\n\nYour 'fc_layers_config' construction option is not correct. """
                                """The first element of the list of nodes in the fc layer must be -1 """
                                """because the input to fc will be set automatically to the size of """
                                """the final activation volume of the convolutional part of the network""")
        if  path_saved_model:
            self.path_saved_model = path_saved_model
        if classes:
            self.class_labels = classes
        if learning_rate:
            self.learning_rate = learning_rate
        else:
            self.learning_rate = 1e-6
        if momentum:
            self.momentum = momentum
        if epochs:
            self.epochs = epochs
        if batch_size:
            self.batch_size = batch_size
        if use_gpu is not None:
            self.use_gpu = use_gpu
            if use_gpu is True:
                if torch.cuda.is_available():
                    self.device = torch.device("cuda:0")
                else: 
                    self.device = torch.device("cpu")
        else:
            self.device = torch.device("cpu")
        if debug_train:                             
            self.debug_train = debug_train
        else:
            self.debug_train = 0
        if debug_test:                             
            self.debug_test = debug_test
        else:
            self.debug_test = 0
        self.debug_config = 0

    def parse_config_string_for_convo_layers(self):
        '''
        Each collection of 'n' otherwise identical layers in a convolutional network is 
        specified by a string that looks like:

                                 "nx[a,b,c,d]-MaxPool(k)"
        where 
                n      =  num of this type of convo layer
                a      =  number of out_channels                      [in_channels determined by prev layer] 
                b,c    =  kernel for this layer is of size (b,c)      [b along height, c along width]
                d      =  stride for convolutions
                k      =  maxpooling over kxk patches with stride of k

        Example:
                     "n1x[a1,b1,c1,d1]-MaxPool(k1)  n2x[a2,b2,c2,d2]-MaxPool(k2)"
        '''
        configuration = self.convo_layers_config
        configs = configuration.split()
        all_convo_layers = []
        image_size_after_layer = self.image_size
        for k,config in enumerate(configs):
            two_parts = config.split('-')
            how_many_conv_layers_with_this_config = int(two_parts[0][:config.index('x')])
            if self.debug_config:
                print("\n\nhow many convo layers with this config: %d" % how_many_conv_layers_with_this_config)
            maxpooling_size = int(re.findall(r'\d+', two_parts[1])[0])
            if self.debug_config:
                print("\nmax pooling size for all convo layers with this config: %d" % maxpooling_size)
            for conv_layer in range(how_many_conv_layers_with_this_config):            
                convo_layer = {'out_channels':None, 
                               'kernel_size':None, 
                               'convo_stride':None, 
                               'maxpool_size':None,
                               'maxpool_stride': None}
                kernel_params = two_parts[0][config.index('x')+1:][1:-1].split(',')
                if self.debug_config:
                    print("\nkernel_params: %s" % str(kernel_params))
                convo_layer['out_channels'] = int(kernel_params[0])
                convo_layer['kernel_size'] = (int(kernel_params[1]), int(kernel_params[2]))
                convo_layer['convo_stride'] =  int(kernel_params[3])
                image_size_after_layer = [x // convo_layer['convo_stride'] for x in image_size_after_layer]
                convo_layer['maxpool_size'] = maxpooling_size
                convo_layer['maxpool_stride'] = maxpooling_size
                image_size_after_layer = [x // convo_layer['maxpool_size'] for x in image_size_after_layer]
                all_convo_layers.append(convo_layer)
        configs_for_all_convo_layers = {i : all_convo_layers[i] for i in range(len(all_convo_layers))}
        if self.debug_config:
            print("\n\nAll convo layers: %s" % str(configs_for_all_convo_layers))
        last_convo_layer = configs_for_all_convo_layers[len(all_convo_layers)-1]
        out_nodes_final_layer = image_size_after_layer[0] * image_size_after_layer[1] * \
                                                                      last_convo_layer['out_channels']
        self.fc_layers_config[0] = out_nodes_final_layer
        self.configs_for_all_convo_layers = configs_for_all_convo_layers
        return configs_for_all_convo_layers


    def build_convo_layers(self, configs_for_all_convo_layers):
        conv_layers = nn.ModuleList()
        in_channels_for_next_layer = None
        for layer_index in configs_for_all_convo_layers:
            if self.debug_config:
                print("\n\n\nLayer index: %d" % layer_index)
            in_channels = 3 if layer_index == 0 else in_channels_for_next_layer
            out_channels = configs_for_all_convo_layers[layer_index]['out_channels']
            kernel_size = configs_for_all_convo_layers[layer_index]['kernel_size']
            padding = tuple((k-1) // 2 for k in kernel_size)
            stride       = configs_for_all_convo_layers[layer_index]['convo_stride']
            maxpool_size = configs_for_all_convo_layers[layer_index]['maxpool_size']
            if self.debug_config:
                print("\n     in_channels=%d   out_channels=%d    kernel_size=%s     stride=%s    \
                maxpool_size=%s" % (in_channels, out_channels, str(kernel_size), str(stride), 
                str(maxpool_size)))
            conv_layers.append( nn.Conv2d( in_channels,out_channels,kernel_size,stride=stride,padding=padding) )
            conv_layers.append( nn.MaxPool2d( maxpool_size ) )
            conv_layers.append( nn.ReLU() ),
            in_channels_for_next_layer = out_channels
        return conv_layers

    def build_fc_layers(self):
        fc_layers = nn.ModuleList()
        for layer_index in range(len(self.fc_layers_config) - 1):
            fc_layers.append( nn.Linear( self.fc_layers_config[layer_index], 
                                                                self.fc_layers_config[layer_index+1] ) )
        return fc_layers            

    def load_cifar_10_dataset(self):       
        '''
        In the code shown below, the call to "ToTensor()" converts the usual int range 0-255 for pixel 
        values to 0-1.0 float vals and then the call to "Normalize()" changes the range to -1.0-1.0 float 
        vals. For additional explanation of the call to "tvt.ToTensor()", see Slide 31 of my Week 2 
        slides at the DL course website.  And see Slides 32 and 33 for the syntax 
        "tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))".  In this call, the three numbers in the
        first tuple change the means in the three color channels and the three numbers in the second 
        tuple change the standard deviations according to the formula:

                 image_channel_val = (image_channel_val - mean) / std

        The end result is that the values in the image tensor will be normalized to fall between -1.0 
        and +1.0. If needed we can do inverse normalization  by

                 image_channel_val  =   (image_channel_val * std) + mean
        '''

        ##   But then the call to Normalize() changes the range to -1.0-1.0 float vals.
        transform = tvt.Compose([tvt.ToTensor(),
                                 tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])    ## accuracy: 51%
        ##  Define where the training and the test datasets are located:
        train_data_loc = torchvision.datasets.CIFAR10(root=self.dataroot, train=True, download=True, transform=transform)
        test_data_loc = torchvision.datasets.CIFAR10(root=self.dataroot, train=False, download=True, transform=transform)
        ##  Now create the data loaders:
        self.train_data_loader = torch.utils.data.DataLoader(train_data_loc,batch_size=self.batch_size, shuffle=True, num_workers=2)
        self.test_data_loader = torch.utils.data.DataLoader(test_data_loc,batch_size=self.batch_size, shuffle=False, num_workers=2)

    def load_cifar_10_dataset_with_augmentation(self):             
        '''
        In general, we want to do data augmentation for training:
        '''
        transform_train = tvt.Compose([
                                  tvt.RandomCrop(32, padding=4),
                                  tvt.RandomHorizontalFlip(),
                                  tvt.ToTensor(),
                                  tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])        
        ##  Don't need any augmentation for the test data: 
        transform_test = tvt.Compose([
                               tvt.ToTensor(),
                               tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        ##  Define where the training and the test datasets are located
        train_data_loc = torchvision.datasets.CIFAR10( root=self.dataroot, train=True, download=True, transform=transform_train )
        test_data_loc = torchvision.datasets.CIFAR10(  root=self.dataroot, train=False, download=True, transform=transform_test )
        ##  Now create the data loaders:
        self.train_data_loader = torch.utils.data.DataLoader(train_data_loc, batch_size=self.batch_size, shuffle=True, num_workers=2)
        self.test_data_loader = torch.utils.data.DataLoader(test_data_loc, batch_size=self.batch_size, shuffle=False, num_workers=2)

    def imshow(self, img):
        '''
        called by display_tensor_as_image() for displaying the image
        '''
        img = img / 2 + 0.5     # unnormalize
        npimg = img.numpy()
        plt.imshow(np.transpose(npimg, (1, 2, 0)))
        plt.show()

    class Net(nn.Module):
        def __init__(self, convo_layers, fc_layers):
            super(DLStudio.Net, self).__init__()
            self.my_modules_convo = convo_layers
            self.my_modules_fc = fc_layers
        def forward(self, x):
            for m in self.my_modules_convo:
                x = m(x)
            x = x.view(x.shape[0], -1)
            for m in self.my_modules_fc:
                x = m(x)
            return x


    def run_code_for_training(self, net, display_images=False):        
        filename_for_out = "performance_numbers_" + str(self.epochs) + ".txt"
        FILE = open(filename_for_out, 'w')
        net = copy.deepcopy(net)
        net = net.to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(net.parameters(), lr=self.learning_rate, momentum=self.momentum)
        print("\n\nStarting training loop...")
        start_time = time.perf_counter()
        loss_tally = []
        elapsed_time = 0.0
        for epoch in range(self.epochs):  
            print("")
            running_loss = 0.0
            for i, data in enumerate(self.train_data_loader):
                inputs, labels = data
                if i % 1000 == 999:
                    current_time = time.perf_counter()
                    elapsed_time = current_time - start_time 
                    print("\n\n[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]   Ground Truth:     " % 
                          (epoch+1, self.epochs, i+1, elapsed_time) + 
                          ' '.join('%10s' % self.class_labels[labels[j]] for j in range(self.batch_size)))
                inputs = inputs.to(self.device)
                labels = labels.to(self.device)
                ##  Since PyTorch likes to construct dynamic computational graphs, we need to
                ##  zero out the previously calculated gradients for the learnable parameters:
                optimizer.zero_grad()
                outputs = net(inputs)
                loss = criterion(outputs, labels)
                running_loss += loss.item()
                if i % 1000 == 999:
                    _, predicted = torch.max(outputs.data, 1)
                    print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]   Predicted Labels: " % 
                     (epoch+1, self.epochs, i+1, elapsed_time ) +
                     ' '.join('%10s' % self.class_labels[predicted[j]] for j in range(self.batch_size)))
                    avg_loss = running_loss / float(1000)
                    loss_tally.append(avg_loss)
                    print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]   Loss: %.3f" % 
                                                                   (epoch+1, self.epochs, i+1, elapsed_time, avg_loss))    
                    FILE.write("%.3f\n" % avg_loss)
                    FILE.flush()
                    running_loss = 0.0
                    if display_images:
                        logger = logging.getLogger()
                        old_level = logger.level
                        logger.setLevel(100)
                        plt.figure(figsize=[6,3])
                        plt.imshow(np.transpose(torchvision.utils.make_grid(inputs,  normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                        plt.show()
                        logger.setLevel(old_level)
                loss.backward()
                optimizer.step()
        print("\nFinished Training\n")
        self.save_model(net)
        plt.figure(figsize=(10,5))
        plt.title("Labeling Loss vs. Iterations")
        plt.plot(loss_tally)
        plt.xlabel("iterations")
        plt.ylabel("loss")
        plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
        plt.savefig("loss_vs_iterations.png")
        plt.show()


    def display_tensor_as_image(self, tensor, title=""):
        '''
        This method converts the argument tensor into a photo image that you can display
        in your terminal screen. It can convert tensors of three different shapes
        into images: (3,H,W), (1,H,W), and (H,W), where H, for height, stands for the
        number of pixels in the vertical direction and W, for width, for the same
        along the horizontal direction.  When the first element of the shape is 3,
        that means that the tensor represents a color image in which each pixel in
        the (H,W) plane has three values for the three color channels.  On the other
        hand, when the first element is 1, that stands for a tensor that will be
        shown as a grayscale image.  And when the shape is just (H,W), that is
        automatically taken to be for a grayscale image.
        '''
        tensor_range = (torch.min(tensor).item(), torch.max(tensor).item())
        if tensor_range == (-1.0,1.0):
            ##  The tensors must be between 0.0 and 1.0 for the display:
            print("\n\n\nimage un-normalization called")
            tensor = tensor/2.0 + 0.5     # unnormalize
        plt.figure(title)
        ###  The call to plt.imshow() shown below needs a numpy array. We must also
        ###  transpose the array so that the number of channels (the same thing as the
        ###  number of color planes) is in the last element.  For a tensor, it would be in
        ###  the first element.
        if tensor.shape[0] == 3 and len(tensor.shape) == 3:
            plt.imshow( tensor.numpy().transpose(1,2,0) )
        ###  If the grayscale image was produced by calling torchvision.transform's
        ###  ".ToPILImage()", and the result converted to a tensor, the tensor shape will
        ###  again have three elements in it, however the first element that stands for
        ###  the number of channels will now be 1
        elif tensor.shape[0] == 1 and len(tensor.shape) == 3:
            tensor = tensor[0,:,:]
            plt.imshow( tensor.numpy(), cmap = 'gray' )
        ###  For any one color channel extracted from the tensor representation of a color
        ###  image, the shape of the tensor will be (W,H):
        elif len(tensor.shape) == 2:
            plt.imshow( tensor.numpy(), cmap = 'gray' )
        else:
            sys.exit("\n\n\nfrom 'display_tensor_as_image()': tensor for image is ill formed -- aborting")
        plt.show()

    def check_a_sampling_of_images(self):
        '''
        Displays the first batch_size number of images in your dataset.
        '''
        dataiter = iter(self.train_data_loader)
        images, labels = dataiter.next()
        # Since negative pixel values make no sense for display, setting the 'normalize' 
        # option to True will change the range back from (-1.0,1.0) to (0.0,1.0):
        self.display_tensor_as_image(torchvision.utils.make_grid(images, normalize=True))
        # Print class labels for the images shown:
        print(' '.join('%5s' % self.class_labels[labels[j]] for j in range(self.batch_size)))

    def save_model(self, model):
        '''
        Save the trained model to a disk file
        '''
        torch.save(model.state_dict(), self.path_saved_model)


    def run_code_for_testing(self, net, display_images=False):
        net.load_state_dict(torch.load(self.path_saved_model))
        net = net.eval()
        net = net.to(self.device)
        ##  In what follows, in addition to determining the predicted label for each test
        ##  image, we will also compute some stats to measure the overall performance of
        ##  the trained network.  This we will do in two different ways: For each class,
        ##  we will measure how frequently the network predicts the correct labels.  In
        ##  addition, we will compute the confusion matrix for the predictions.
        filename_for_results = "classification_results_" + str(self.epochs) + ".txt"
        FILE = open(filename_for_results, 'w')
        correct = 0
        total = 0
        confusion_matrix = torch.zeros(len(self.class_labels), len(self.class_labels))
        class_correct = [0] * len(self.class_labels)
        class_total = [0] * len(self.class_labels)
        with torch.no_grad():
            for i,data in enumerate(self.test_data_loader):
                ##  data is set to the images and the labels for one batch at a time:
                images, labels = data
                images = images.to(self.device)
                labels = labels.to(self.device)
                if i % 1000 == 999:
                    print("\n\n[i=%d:] Ground Truth:     " % (i+1) + ' '.join('%5s' % self.class_labels[labels[j]] for j in range(self.batch_size)))
                outputs = net(images)
                ##  max() returns two things: the max value and its index in the 10 element
                ##  output vector.  We are only interested in the index --- since that is 
                ##  essentially the predicted class label:
                _, predicted = torch.max(outputs.data, 1)#
                if i % 1000 == 999:
                    print("[i=%d:] Predicted Labels: " % (i+1) + ' '.join('%5s' % self.class_labels[predicted[j]] for j in range(self.batch_size)))
                    logger = logging.getLogger()
                    old_level = logger.level
                    if display_images:
                        logger.setLevel(100)
                        plt.figure(figsize=[6,3])
                        plt.imshow(np.transpose(torchvision.utils.make_grid(images, normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                        plt.show()
                        logger.setLevel(old_level)
                for label,prediction in zip(labels,predicted):
                        confusion_matrix[label][prediction] += 1
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                ##  comp is a list of size batch_size of "True" and "False" vals
                comp = predicted == labels       
                for j in range(self.batch_size):
                    label = labels[j]
                    ##  The following works because, in a numeric context, the boolean value
                    ##  "False" is the same as number 0 and the boolean value True is the 
                    ##  same as number 1. For that reason "4 + True" will evaluate to 5 and
                    ##  "4 + False" will evaluate to 4.  Also, "1 == True" evaluates to "True"
                    ##  "1 == False" evaluates to "False".  However, note that "1 is True" 
                    ##  evaluates to "False" because the operator "is" does not provide a 
                    ##  numeric context for "True". And so on.  In the statement that follows,
                    ##  while  c[j].item() will either return "False" or "True", for the 
                    ##  addition operator, Python will use the values 0 and 1 instead.
                    class_correct[label] += comp[j].item()
                    class_total[label] += 1
        for j in range(len(self.class_labels)):
            print('Prediction accuracy for %5s : %2d %%' % (self.class_labels[j], 100 * class_correct[j] / class_total[j]))
            FILE.write('\n\nPrediction accuracy for %5s : %2d %%\n' % (self.class_labels[j], 100 * class_correct[j] / class_total[j]))
        print("\n\n\nOverall accuracy of the network on the 10000 test images: %d %%" % (100 * correct / float(total)))
        FILE.write("\n\n\nOverall accuracy of the network on the 10000 test images: %d %%\n" % (100 * correct / float(total)))
        print("\n\nDisplaying the confusion matrix:\n")
        FILE.write("\n\nDisplaying the confusion matrix:\n\n")
        out_str = "         "
        for j in range(len(self.class_labels)):  out_str +=  "%7s" % self.class_labels[j]   
        print(out_str + "\n")
        FILE.write(out_str + "\n\n")
        for i,label in enumerate(self.class_labels):
            out_percents = [100 * confusion_matrix[i,j] / float(class_total[i]) 
                                                      for j in range(len(self.class_labels))]
            out_percents = ["%.2f" % item.item() for item in out_percents]
            out_str = "%6s:  " % self.class_labels[i]
            for j in range(len(self.class_labels)): out_str +=  "%7s" % out_percents[j]
            print(out_str)
            FILE.write(out_str + "\n")
        FILE.close()        


    ###%%%
    #####################################################################################################################
    #############################  Start Definition of Inner Class ExperimentsWithSequential ############################

    class ExperimentsWithSequential(nn.Module):                                
        """
        Demonstrates how to use the torch.nn.Sequential container class

        Class Path:  DLStudio  ->  ExperimentsWithSequential    
        """
        def __init__(self, dl_studio ):
            super(DLStudio.ExperimentsWithSequential, self).__init__()
            self.dl_studio = dl_studio

        def load_cifar_10_dataset(self):       
            self.dl_studio.load_cifar_10_dataset()

        def load_cifar_10_dataset_with_augmentation(self):             
            self.dl_studio.load_cifar_10_dataset_with_augmentation()

        class Net(nn.Module):
            """
            To see if the DLStudio class would work with any network that a user may
            want to experiment with, I copy-and-pasted the network shown below
            from Zhenye's GitHub blog: https://github.com/Zhenye-Na/blog

            Class Path:  DLStudio  ->  ExperimentsWithSequential  ->  Net
            """
            def __init__(self):
                super(DLStudio.ExperimentsWithSequential.Net, self).__init__()
                self.conv_seqn = nn.Sequential(
                    # Conv Layer block 1:
                    nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
                    nn.BatchNorm2d(32),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    # Conv Layer block 2:
                    nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
                    nn.BatchNorm2d(128),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                    nn.Dropout2d(p=0.05),
                    # Conv Layer block 3:
                    nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
                    nn.BatchNorm2d(256),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.MaxPool2d(kernel_size=2, stride=2),
                )
                self.fc_seqn = nn.Sequential(
                    nn.Dropout(p=0.1),
                    nn.Linear(4096, 1024),
                    nn.ReLU(inplace=True),
                    nn.Linear(1024, 512),
                    nn.ReLU(inplace=True),
                    nn.Dropout(p=0.1),
                    nn.Linear(512, 10)
                )
    
            def forward(self, x):
                x = self.conv_seqn(x)
                # flatten
                x = x.view(x.shape[0], -1)
                x = self.fc_seqn(x)
                return x

        def run_code_for_training(self, net):        
            self.dl_studio.run_code_for_training(net)

        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)

        def run_code_for_testing(self, model):
            self.dl_studio.run_code_for_testing(model)


    ###%%%
    #####################################################################################################################
    ###############################  Start Definition of Inner Class ExperimentsWithCIFAR ###############################

    class ExperimentsWithCIFAR(nn.Module):              
        """
        Class Path:  DLStudio  ->  ExperimentsWithCIFAR
        """

        def __init__(self, dl_studio ):
            super(DLStudio.ExperimentsWithCIFAR, self).__init__()
            self.dl_studio = dl_studio

        def load_cifar_10_dataset(self):       
            self.dl_studio.load_cifar_10_dataset()

        def load_cifar_10_dataset_with_augmentation(self):             
            self.dl_studio.load_cifar_10_dataset_with_augmentation()

        ##  You can instantiate two different types of networks when experimenting with 
        ##  the inner class ExperimentsWithCIFAR.  The network shown below is from the 
        ##  PyTorch tutorial
        ##
        ##     https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
        ##
        class Net(nn.Module):
            """
            Class Path:  DLStudio  ->  ExperimentsWithCIFAR  ->  Net
            """
            def __init__(self):
                super(DLStudio.ExperimentsWithCIFAR.Net, self).__init__()
                self.conv1 = nn.Conv2d(3, 6, 5)
                self.conv2 = nn.Conv2d(6, 16, 5)
                self.fc1 = nn.Linear(16 * 5 * 5, 120)
                self.fc2 = nn.Linear(120, 84)
                self.fc3 = nn.Linear(84, 10)
        
            def forward(self, x):
                x = nn.MaxPool2d(2,2)(F.relu(self.conv1(x)))
                x = nn.MaxPool2d(2,2)(F.relu(self.conv2(x)))
                x  =  x.view( x.shape[0], - 1 )
                x = F.relu(self.fc1(x))
                x = F.relu(self.fc2(x))
                x = self.fc3(x)
                return x

        ##  Instead of using the network shown above, you can also use the network shown below.
        ##  if you are playing with the ExperimentsWithCIFAR inner class. If that's what you
        ##  want to do, in the script "playing_with_cifar10.py" in the Examples directory,
        ##  you will need to replace the statement
        ##                          model = exp_cifar.Net()
        ##  by the statement
        ##                          model = exp_cifar.Net2()        
        ##
        class Net2(nn.Module):
            """
            Class Path:  DLStudio  ->  ExperimentsWithCIFAR  ->  Net2
            """
            def __init__(self):
                """
                I created this network class just to see if it was possible to simply calculate
                the size of the first of the fully connected layers from strides in the convo
                layers up to that point and from the out_channels used in the top-most convo 
                layer.   In what you see below, I am keeping track of all the strides by pushing 
                them into the array 'strides'.  Subsequently, in the formula shown in line (A),
                I use the product of all strides and the number of out_channels for the topmost
                layer to compute the size of the first fully-connected layer.
                """
                super(DLStudio.ExperimentsWithCIFAR.Net2, self).__init__()
                self.relu = nn.ReLU()
                strides = []
                patch_size = 2
                ## conv1:
                out_ch, ker_size, conv_stride, pool_stride = 128,5,1,2
                self.conv1 = nn.Conv2d(3, out_ch, (ker_size,ker_size), padding=(ker_size-1)//2)     
                self.pool1 = nn.MaxPool2d(patch_size, pool_stride)     
                strides += (conv_stride, pool_stride)
                ## conv2:
                in_ch = out_ch
                out_ch, ker_size, conv_stride, pool_stride = 128,3,1,2
                self.conv2 = nn.Conv2d(in_ch, out_ch, ker_size, padding=(ker_size-1)//2)
                self.pool2 = nn.MaxPool2d(patch_size, pool_stride)     
                strides += (conv_stride, pool_stride)
                ## conv3:                   
                in_ch = out_ch
                out_ch, ker_size, conv_stride, pool_stride = in_ch,2,1,1
                self.conv3 = nn.Conv2d(in_ch, out_ch, ker_size, padding=1)
                self.pool3 = nn.MaxPool2d(patch_size, pool_stride)         
                ## figure out the number of nodes needed for entry into fc:
                in_size_for_fc = out_ch * (32 // np.prod(strides)) ** 2                    ## (A)
                self.in_size_for_fc = in_size_for_fc
                self.fc1 = nn.Linear(in_size_for_fc, 150)
                self.fc2 = nn.Linear(150, 100)
                self.fc3 = nn.Linear(100, 10)
        
            def forward(self, x):
                ##  We know that forward() begins its with work x shaped as (4,3,32,32) where
                ##  4 is the batch size, 3 in_channels, and where the input image size is 32x32.
                x = self.relu(self.conv1(x))  
                x = self.pool1(x)             
                x = self.relu(self.conv2(x))
                x = self.pool2(x)             
                x = self.pool3(self.relu(self.conv3(x)))
                x  =  x.view( x.shape[0], - 1 )
                x = self.relu(self.fc1( x ))
                x = self.relu(self.fc2( x ))
                x = self.fc3(x)
                return x

        def run_code_for_training(self, net, display_images=False):
            self.dl_studio.run_code_for_training(net, display_images)
            
        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)

        def run_code_for_testing(self, model, display_images=False):
            self.dl_studio.run_code_for_testing(model, display_images)


    ###%%%
    #####################################################################################################################
    #######################  Start Definition of Inner Class BMEnet for Illustrating Skip Connections  ##################

    class BMEnet(nn.Module):
        """
        This educational class is meant for illustrating the concepts related to the 
        use of skip connections in neural network.  It is now well known that deep
        networks are difficult to train because of the vanishing gradients problem.
        What that means is that as the depth of network increases, the loss gradients
        calculated for the early layers become more and more muted, which suppresses
        the learning of the parameters in those layers.  An important mitigation
        strategy for addressing this problem consists of creating a CNN using blocks
        with skip connections.

        With the code shown in this inner class of the module, you can now experiment with
        skip connections in a CNN to see how a deep network with this feature might improve
        the classification results.  As you will see in the code shown below, the network
        that allows you to construct a CNN with skip connections is named BMEnet.  As shown
        in the script playing_with_skip_connections.py in the Examples directory of the
        distribution, you can easily create a CNN with arbitrary depth just by using the
        "depth" constructor option for the BMEnet class.  The basic block of the network
        constructed by BMEnet is called SkipBlock which, very much like the BasicBlock in
        ResNet-18, has a couple of convolutional layers whose output is combined with the
        input to the block.
    
        Note that the value given to the "depth" constructor option for the BMEnet class
        does NOT translate directly into the actual depth of the CNN. [Again, see the script
        playing_with_skip_connections.py in the Examples directory for how to use this
        option.] The value of "depth" is translated into how many "same input and output
        channels" and the "same input and output sizes" instances of SkipBlock to use
        between successive instances of downsampling and channel-doubling instances of
        SkipBlock.
 
        Class Path: DLStudio -> BMEnet
        """
        def __init__(self, dl_studio, skip_connections=True, depth=8):
            super(DLStudio.BMEnet, self).__init__()
            self.dl_studio = dl_studio
            self.depth = depth
            image_size = dl_studio.image_size
            num_ds = 0                                 ## num_ds stands for number of downsampling steps
            self.conv = nn.Conv2d(3, 64, 3, padding=1)
            self.skip64_arr = nn.ModuleList()
            for i in range(self.depth):
                self.skip64_arr.append(DLStudio.BMEnet.SkipBlock(64, 64, skip_connections=skip_connections))
            self.skip64to128ds = DLStudio.BMEnet.SkipBlock(64, 128, downsample=True, skip_connections=skip_connections )
            num_ds += 1              
            self.skip128_arr = nn.ModuleList()
            for i in range(self.depth):
                self.skip128_arr.append(DLStudio.BMEnet.SkipBlock(128, 128, skip_connections=skip_connections))
            self.skip128to256ds = DLStudio.BMEnet.SkipBlock(128, 256, downsample=True, skip_connections=skip_connections )
            num_ds += 1
            self.skip256_arr = nn.ModuleList()
            for i in range(self.depth):
                self.skip256_arr.append(DLStudio.BMEnet.SkipBlock(256, 256, skip_connections=skip_connections))
            self.fc1 =  nn.Linear( (image_size[0]// (2 ** num_ds))  *  (image_size[1]//(2 ** num_ds))  * 256, 1000)
            self.fc2 =  nn.Linear(1000, 10)

        def forward(self, x):
            x = nn.functional.relu(self.conv(x))          
            for skip64 in self.skip64_arr:
                x = skip64(x)                
            x = self.skip64to128ds(x)
            for skip128 in self.skip128_arr:
                x = skip128(x)                
            x = self.skip128to256ds(x)
            for skip256 in self.skip256_arr:
                x = skip256(x)                
            x  =  x.view( x.shape[0], - 1 )
            x = nn.functional.relu(self.fc1(x))
            x = self.fc2(x)
            return x            


        def load_cifar_10_dataset(self):       
            self.dl_studio.load_cifar_10_dataset()

        def load_cifar_10_dataset_with_augmentation(self):             
            self.dl_studio.load_cifar_10_dataset_with_augmentation()


        class SkipBlock(nn.Module):
            """
            Class Path:   DLStudio  ->  BMEnet  ->  SkipBlock
            """            
            def __init__(self, in_ch, out_ch, downsample=False, skip_connections=True):
                super(DLStudio.BMEnet.SkipBlock, self).__init__()
                self.downsample = downsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convo1 = nn.Conv2d(in_ch, in_ch, 3, stride=1, padding=1)
                self.convo2 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.bn1 = nn.BatchNorm2d(in_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                self.in2out  =  nn.Conv2d(in_ch, out_ch, 1)       
                if downsample:
                    ##  Setting stride to 2 and kernel_size to 1 amounts to retaining every
                    ##  other pixel in the image --- which halves the size of the image:
                    self.downsampler1 = nn.Conv2d(in_ch, in_ch, 1, stride=2)
                    self.downsampler2 = nn.Conv2d(out_ch, out_ch, 1, stride=2)

            def forward(self, x):
                identity = x                                     
                out = self.convo1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                out = self.convo2(out)                              
                out = self.bn2(out)                              
                out = nn.functional.relu(out)
                if self.downsample:
                    identity = self.downsampler1(identity)
                    out = self.downsampler2(out)
                if self.skip_connections:
                    if (self.in_ch == self.out_ch) and (self.downsample is False):
                        out = out + identity
                    elif (self.in_ch != self.out_ch) and (self.downsample is False):
                        identity = self.in2out( identity )     
                        out = out + identity
                    elif (self.in_ch != self.out_ch) and (self.downsample is True):
                        out = out + torch.cat((identity, identity), dim=1)
                return out

        def run_code_for_training(self, net, display_images=False):        
            self.dl_studio.run_code_for_training(net, display_images)
            
        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)

        def run_code_for_testing(self, model, display_images=False):
            self.dl_studio.run_code_for_testing(model, display_images=False)


    ###%%%
    #####################################################################################################################
    ################################  Start Definition of Inner Class CustomDataLoading  ################################

    class CustomDataLoading(nn.Module):             
        """
        This is a testbed for experimenting with a completely grounds-up attempt at
        designing a custom data loader.  Ordinarily, if the basic format of how the dataset
        is stored is similar to one of the datasets that the Torchvision module knows about,
        you can go ahead and use that for your own dataset.  At worst, you may need to carry
        out some light customizations depending on the number of classes involved, etc.

        However, if the underlying dataset is stored in a manner that does not look like
        anything in Torchvision, you have no choice but to supply yourself all of the data
        loading infrastructure.  That is what this inner class of the main DLStudio class 
        is all about.

        The custom data loading exercise here is related to a dataset called PurdueShapes5
        that contains 32x32 images of binary shapes belonging to the following five classes:

                       1.  rectangle
                       2.  triangle
                       3.  disk
                       4.  oval
                       5.  star

        The dataset was generated by randomizing the sizes and the orientations of these
        five patterns.  Since the patterns are rotated with a very simple non-interpolating
        transform, just the act of random rotations can introduce boundary and even interior
        noise in the patterns.

        Each 32x32 image is stored in the dataset as the following list:

                           [R, G, B, Bbox, Label]
        where
                R     :   is a 1024 element list of the values for the red component
                          of the color at all the pixels
           
                B     :   the same as above but for the green component of the color

                G     :   the same as above but for the blue component of the color

                Bbox  :   a list like [x1,y1,x2,y2] that defines the bounding box 
                          for the object in the image
           
                Label :   the shape of the object

        I serialize the dataset with Python's pickle module and then compress it with the
        gzip module.

        You will find the following dataset directories in the "data" subdirectory of
        Examples in the DLStudio distro:

               PurdueShapes5-10000-train.gz
               PurdueShapes5-1000-test.gz
               PurdueShapes5-20-train.gz
               PurdueShapes5-20-test.gz               

        The number that follows the main name string "PurdueShapes5-" is for the number of
        images in the dataset.

        You will find the last two datasets, with 20 images each, useful for debugging your
        logic for object detection and bounding-box regression.

        Class Path:   DLStudio  ->  CustomDataLoading
        """     
        def __init__(self, dl_studio, dataserver_train=None, dataserver_test=None, dataset_file_train=None, dataset_file_test=None):
            super(DLStudio.CustomDataLoading, self).__init__()
            self.dl_studio = dl_studio
            self.dataserver_train = dataserver_train
            self.dataserver_test = dataserver_test

        class PurdueShapes5Dataset(torch.utils.data.Dataset):
            """
            Class Path:   DLStudio  ->  CustomDataLoading  ->  PurdueShapes5Dataset
            """
            def __init__(self, dl_studio, train_or_test, dataset_file):
                super(DLStudio.CustomDataLoading.PurdueShapes5Dataset, self).__init__()
                if train_or_test == 'train' and dataset_file == "PurdueShapes5-10000-train.gz":
                    if os.path.exists("torch_saved_PurdueShapes5-10000_dataset.pt") and \
                              os.path.exists("torch_saved_PurdueShapes5_label_map.pt"):
                        print("\nLoading training data from the torch-saved archive")
                        self.dataset = torch.load("torch_saved_PurdueShapes5-10000_dataset.pt")
                        self.label_map = torch.load("torch_saved_PurdueShapes5_label_map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                    else: 
                        print("""\n\n\nLooks like this is the first time you will be loading in\n"""
                              """the dataset for this script. First time loading could take\n"""
                              """a minute or so.  Any subsequent attempts will only take\n"""
                              """a few seconds.\n\n\n""")
                        root_dir = dl_studio.dataroot
                        f = gzip.open(root_dir + dataset_file, 'rb')
                        dataset = f.read()
                        self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                        torch.save(self.dataset, "torch_saved_PurdueShapes5-10000_dataset.pt")
                        torch.save(self.label_map, "torch_saved_PurdueShapes5_label_map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                else:
                    root_dir = dl_studio.dataroot
                    f = gzip.open(root_dir + dataset_file, 'rb')
                    dataset = f.read()
                    self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                    # reverse the key-value pairs in the label dictionary:
                    self.class_labels = dict(map(reversed, self.label_map.items()))
             
            def __len__(self):
                return len(self.dataset)

            def __getitem__(self, idx):
                r = np.array( self.dataset[idx][0] )
                g = np.array( self.dataset[idx][1] )
                b = np.array( self.dataset[idx][2] )
                R,G,B = r.reshape(32,32), g.reshape(32,32), b.reshape(32,32)
                im_tensor = torch.zeros(3,32,32, dtype=torch.float)
                im_tensor[0,:,:] = torch.from_numpy(R)
                im_tensor[1,:,:] = torch.from_numpy(G)
                im_tensor[2,:,:] = torch.from_numpy(B)
                sample = {'image' : im_tensor, 
                          'bbox' : self.dataset[idx][3],                          
                          'label' : self.dataset[idx][4] }
                return sample

        def load_PurdueShapes5_dataset(self, dataserver_train, dataserver_test ):       
            transform = tvt.Compose([tvt.ToTensor(),
                                tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])  
            self.train_dataloader = torch.utils.data.DataLoader(dataserver_train,
                               batch_size=self.dl_studio.batch_size,shuffle=True, num_workers=4)
            self.test_dataloader = torch.utils.data.DataLoader(dataserver_test,
                               batch_size=self.dl_studio.batch_size,shuffle=False, num_workers=4)


        class ECEnet(nn.Module):
            """
     
            Class Path: DLStudio -> CustomDataloading -> ECEnet
    
            """
            def __init__(self, dl_studio, skip_connections=True, depth=8):
                super(DLStudio.CustomDataLoading.ECEnet, self).__init__()
                self.dl_studio = dl_studio
                self.depth = depth
                image_size = dl_studio.image_size
                num_ds = 0                                 ## num_ds stands for number of downsampling steps
                self.conv = nn.Conv2d(3, 64, 3, padding=1)
                self.skip64_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip64_arr.append(DLStudio.CustomDataLoading.SkipBlock2(64, 64, skip_connections=skip_connections))
                self.skip64to128ds = DLStudio.CustomDataLoading.SkipBlock2(64, 128, downsample=True, skip_connections=skip_connections )
                num_ds += 1              
                self.skip128_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip128_arr.append(DLStudio.CustomDataLoading.SkipBlock2(128, 128, skip_connections=skip_connections))
                self.skip128to256ds = DLStudio.CustomDataLoading.SkipBlock2(128, 256, downsample=True, skip_connections=skip_connections )
                num_ds += 1
                self.skip256_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip256_arr.append(DLStudio.CustomDataLoading.SkipBlock2(256, 256, skip_connections=skip_connections))
                self.fc1 =  nn.Linear( (image_size[0]// (2 ** num_ds))  *  (image_size[1]//(2 ** num_ds))  * 256, 1000)
                self.fc2 =  nn.Linear(1000, 10)
    
            def forward(self, x):
                x = nn.functional.relu(self.conv(x))          
                for skip64 in self.skip64_arr:
                    x = skip64(x)                
                x = self.skip64to128ds(x)
                for skip128 in self.skip128_arr:
                    x = skip128(x)                
                x = self.skip128to256ds(x)
                for skip256 in self.skip256_arr:
                    x = skip256(x)                
                x  =  x.view( x.shape[0], - 1 )
                x = nn.functional.relu(self.fc1(x))
                x = self.fc2(x)
                return x            
    
    
            def load_cifar_10_dataset(self):       
                self.dl_studio.load_cifar_10_dataset()
    
            def load_cifar_10_dataset_with_augmentation(self):             
                self.dl_studio.load_cifar_10_dataset_with_augmentation()
    
    
        class SkipBlock2(nn.Module):
            """
            Class Path:   DLStudio  ->  CustomDataloading  ->  SkipBlock
            """            
            def __init__(self, in_ch, out_ch, downsample=False, skip_connections=True):
                super(DLStudio.CustomDataLoading.SkipBlock2, self).__init__()
                self.downsample = downsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convo1 = nn.Conv2d(in_ch, in_ch, 3, stride=1, padding=1)
                self.convo2 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.bn1 = nn.BatchNorm2d(in_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                self.in2out  =  nn.Conv2d(in_ch, out_ch, 1)       
                if downsample:
                    ##  Setting stride to 2 and kernel_size to 1 amounts to retaining every
                    ##  other pixel in the image --- which halves the size of the image:
                    self.downsampler1 = nn.Conv2d(in_ch, in_ch, 1, stride=2)
                    self.downsampler2 = nn.Conv2d(out_ch, out_ch, 1, stride=2)

            def forward(self, x):
                identity = x                                     
                out = self.convo1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                out = self.convo2(out)                              
                out = self.bn2(out)                              
                out = nn.functional.relu(out)
                if self.downsample:
                    identity = self.downsampler1(identity)
                    out = self.downsampler2(out)
                if self.skip_connections:
                    if (self.in_ch == self.out_ch) and (self.downsample is False):
                        out = out + identity
                    elif (self.in_ch != self.out_ch) and (self.downsample is False):
                        identity = self.in2out( identity )     
                        out = out + identity
                    elif (self.in_ch != self.out_ch) and (self.downsample is True):
                        out = out + torch.cat((identity, identity), dim=1)
                return out
    

        def run_code_for_training_with_custom_loading(self, net):        
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net = copy.deepcopy(net)
            net = net.to(self.dl_studio.device)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            for epoch in range(self.dl_studio.epochs):  
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):
                    inputs, bounding_box, labels = data['image'], data['bbox'], data['label']
                    if self.dl_studio.debug_train and i % 1000 == 999:
                        print("\n\n\nlabels: %s" % str(labels))
                        print("\n\n\ntype of labels: %s" % type(labels))
                        print("\n\n[iter=%d:] Ground Truth:     " % (i+1) + 
                        ' '.join('%5s' % self.dataserver_train.class_labels[labels[j].item()] for j in range(self.dl_studio.batch_size)))
                    inputs = inputs.to(self.dl_studio.device)
                    labels = labels.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    outputs = net(inputs)
                    loss = criterion(outputs, labels)
                    if self.dl_studio.debug_train and i % 1000 == 999:
                        _, predicted = torch.max(outputs.data, 1)
                        print("[iter=%d:] Predicted Labels: " % (i+1) + 
                         ' '.join('%5s' % self.dataserver.class_labels[predicted[j]] 
                                           for j in range(self.dl_studio.batch_size)))
                        self.dl_studio.display_tensor_as_image(torchvision.utils.make_grid(
             inputs, normalize=True), "see terminal for TRAINING results at iter=%d" % (i+1))
                    loss.backward()
                    optimizer.step()
                    running_loss += loss.item()
                    if i % 1000 == 999:    
                        avg_loss = running_loss / float(1000)
                        print("[epoch:%d, batch:%5d] loss: %.3f" % (epoch + 1, i + 1, avg_loss))
                        FILE.write("%.3f\n" % avg_loss)
                        FILE.flush()
                        running_loss = 0.0
            print("\nFinished Training\n")
            self.save_model(net)
            
        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)

        def run_code_for_testing_with_custom_loading(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            correct = 0
            total = 0
            confusion_matrix = torch.zeros(len(self.dataserver_train.class_labels), 
                                           len(self.dataserver_train.class_labels))
            class_correct = [0] * len(self.dataserver_train.class_labels)
            class_total = [0] * len(self.dataserver_train.class_labels)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    images, bounding_box, labels = data['image'], data['bbox'], data['label']
                    labels = labels.tolist()
                    if self.dl_studio.debug_test and i % 1000 == 0:
                        print("\n\n[i=%d:] Ground Truth:     " %i + ' '.join('%10s' % 
                          self.dataserver_train.class_labels[labels[j]] for j in range(self.dl_studio.batch_size)))
                    outputs = net(images)
                    ##  max() returns two things: the max value and its index in the 10 element
                    ##  output vector.  We are only interested in the index --- since that is 
                    ##  essentially the predicted class label:
                    _, predicted = torch.max(outputs.data, 1)
                    predicted = predicted.tolist()
                    if self.dl_studio.debug_test and i % 1000 == 0:
                        print("[i=%d:] Predicted Labels: " %i + ' '.join('%10s' % 
                          self.dataserver_train.class_labels[predicted[j]] for j in range(self.dl_studio.batch_size)))
                        self.dl_studio.display_tensor_as_image(
                              torchvision.utils.make_grid(images, normalize=True), 
                              "see terminal for test results at i=%d" % i)
                    for label,prediction in zip(labels,predicted):
                        confusion_matrix[label][prediction] += 1
                    total += len(labels)
                    correct +=  [predicted[ele] == labels[ele] for ele in range(len(predicted))].count(True)
                    comp = [predicted[ele] == labels[ele] for ele in range(len(predicted))]
                    for j in range(self.dl_studio.batch_size):
                        label = labels[j]
                        class_correct[label] += comp[j]
                        class_total[label] += 1
            print("\n")
            for j in range(len(self.dataserver_train.class_labels)):
                print('Prediction accuracy for %5s : %2d %%' % (
              self.dataserver_train.class_labels[j], 100 * class_correct[j] / class_total[j]))
            print("\n\n\nOverall accuracy of the network on the 10000 test images: %d %%" % 
                                                                   (100 * correct / float(total)))
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                "
            for j in range(len(self.dataserver_train.class_labels)):  
                                 out_str +=  "%15s" % self.dataserver_train.class_labels[j]   
            print(out_str + "\n")
            for i,label in enumerate(self.dataserver_train.class_labels):
                out_percents = [100 * confusion_matrix[i,j] / float(class_total[i]) 
                                 for j in range(len(self.dataserver_train.class_labels))]
                out_percents = ["%.2f" % item.item() for item in out_percents]
                out_str = "%12s:  " % self.dataserver_train.class_labels[i]
                for j in range(len(self.dataserver_train.class_labels)): 
                                                       out_str +=  "%15s" % out_percents[j]
                print(out_str)
    
    ###%%%
    #####################################################################################################################
    ##################################  Start Definition of Inner Class DetectAndLocalize  ##############################

    class DetectAndLocalize(nn.Module):             
        """
        The purpose of this inner class is to focus on object detection in images --- as
        opposed to image classification.  Most people would say that object detection is a
        more challenging problem than image classification because, in general, the former
        also requires localization.  The simplest interpretation of what is meant by
        localization is that the code that carries out object detection must also output a
        bounding-box rectangle for the object that was detected.

        You will find in this inner class some examples of LOADnet classes meant for solving
        the object detection and localization problem.  The acronym "LOAD" in "LOADnet"
        stands for

                    "LOcalization And Detection"

        The different network examples included here are LOADnet1, LOADnet2, and LOADnet3.
        For now, only pay attention to LOADnet2 since that's the class I have worked with
        the most for the 1.0.7 distribution.

        Class Path:   DLStudio  ->  DetectAndLocalize
        """
        def __init__(self, dl_studio, dataserver_train=None, dataserver_test=None, dataset_file_train=None, dataset_file_test=None):
            super(DLStudio.DetectAndLocalize, self).__init__()
            self.dl_studio = dl_studio
            self.dataserver_train = dataserver_train
            self.dataserver_test = dataserver_test
            self.debug = False

        class PurdueShapes5Dataset(torch.utils.data.Dataset):
            """
            Class Path:   DLStudio  ->  DetectAndLocalize  ->  PurdueShapes5Dataset
            """
            def __init__(self, dl_studio, train_or_test, dataset_file):
                super(DLStudio.DetectAndLocalize.PurdueShapes5Dataset, self).__init__()
                if train_or_test == 'train' and dataset_file == "PurdueShapes5-10000-train.gz":
                    if os.path.exists("torch-saved-PurdueShapes5-10000-dataset.pt") and \
                              os.path.exists("torch-saved-PurdueShapes5-label-map.pt"):
                        print("\nLoading training data from the torch-saved archive")
                        self.dataset = torch.load("torch-saved-PurdueShapes5-10000-dataset.pt")
                        self.label_map = torch.load("torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                    else: 
                        print("""\n\n\nLooks like this is the first time you will be loading in\n"""
                              """the dataset for this script. First time loading could take\n"""
                              """a minute or so.  Any subsequent attempts will only take\n"""
                              """a few seconds.\n\n\n""")
                        root_dir = dl_studio.dataroot
                        f = gzip.open(root_dir + dataset_file, 'rb')
                        dataset = f.read()
                        if sys.version_info[0] == 3:
                            self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                        else:
                            self.dataset, self.label_map = pickle.loads(dataset)
                        torch.save(self.dataset, "torch-saved-PurdueShapes5-10000-dataset.pt")
                        torch.save(self.label_map, "torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                elif train_or_test == 'train' and dataset_file == "PurdueShapes5-10000-train-noise-20.gz":
                    if os.path.exists("torch-saved-PurdueShapes5-10000-dataset-noise-20.pt") and \
                              os.path.exists("torch-saved-PurdueShapes5-label-map.pt"):
                        print("\nLoading training data from the torch-saved archive")
                        self.dataset = torch.load("torch-saved-PurdueShapes5-10000-dataset-noise-20.pt")
                        self.label_map = torch.load("torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                    else: 
                        print("""\n\n\nLooks like this is the first time you will be loading in\n"""
                              """the dataset for this script. First time loading could take\n"""
                              """a minute or so.  Any subsequent attempts will only take\n"""
                              """a few seconds.\n\n\n""")
                        root_dir = dl_studio.dataroot
                        f = gzip.open(root_dir + dataset_file, 'rb')
                        dataset = f.read()
                        if sys.version_info[0] == 3:
                            self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                        else:
                            self.dataset, self.label_map = pickle.loads(dataset)
                        torch.save(self.dataset, "torch-saved-PurdueShapes5-10000-dataset-noise-20.pt")
                        torch.save(self.label_map, "torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                elif train_or_test == 'train' and dataset_file == "PurdueShapes5-10000-train-noise-50.gz":
                    if os.path.exists("torch-saved-PurdueShapes5-10000-dataset-noise-50.pt") and \
                              os.path.exists("torch-saved-PurdueShapes5-label-map.pt"):
                        print("\nLoading training data from the torch-saved archive")
                        self.dataset = torch.load("torch-saved-PurdueShapes5-10000-dataset-noise-50.pt")
                        self.label_map = torch.load("torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                    else: 
                        print("""\n\n\nLooks like this is the first time you will be loading in\n"""
                              """the dataset for this script. First time loading could take\n"""
                              """a minute or so.  Any subsequent attempts will only take\n"""
                              """a few seconds.\n\n\n""")
                        root_dir = dl_studio.dataroot
                        f = gzip.open(root_dir + dataset_file, 'rb')
                        dataset = f.read()
                        if sys.version_info[0] == 3:
                            self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                        else:
                            self.dataset, self.label_map = pickle.loads(dataset)
                        torch.save(self.dataset, "torch-saved-PurdueShapes5-10000-dataset-noise-50.pt")
                        torch.save(self.label_map, "torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                elif train_or_test == 'train' and dataset_file == "PurdueShapes5-10000-train-noise-80.gz":
                    if os.path.exists("torch-saved-PurdueShapes5-10000-dataset-noise-80.pt") and \
                              os.path.exists("torch-saved-PurdueShapes5-label-map.pt"):
                        print("\nLoading training data from the torch-saved archive")
                        self.dataset = torch.load("torch-saved-PurdueShapes5-10000-dataset-noise-80.pt")
                        self.label_map = torch.load("torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                    else: 
                        print("""\n\n\nLooks like this is the first time you will be loading in\n"""
                              """the dataset for this script. First time loading could take\n"""
                              """a minute or so.  Any subsequent attempts will only take\n"""
                              """a few seconds.\n\n\n""")
                        root_dir = dl_studio.dataroot
                        f = gzip.open(root_dir + dataset_file, 'rb')
                        dataset = f.read()
                        if sys.version_info[0] == 3:
                            self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                        else:
                            self.dataset, self.label_map = pickle.loads(dataset)
                        torch.save(self.dataset, "torch-saved-PurdueShapes5-10000-dataset-noise-80.pt")
                        torch.save(self.label_map, "torch-saved-PurdueShapes5-label-map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                else:
                    root_dir = dl_studio.dataroot
                    f = gzip.open(root_dir + dataset_file, 'rb')
                    dataset = f.read()
                    if sys.version_info[0] == 3:
                        self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                    else:
                        self.dataset, self.label_map = pickle.loads(dataset)
                    # reverse the key-value pairs in the label dictionary:
                    self.class_labels = dict(map(reversed, self.label_map.items()))
             
            def __len__(self):
                return len(self.dataset)

            def __getitem__(self, idx):
                r = np.array( self.dataset[idx][0] )
                g = np.array( self.dataset[idx][1] )
                b = np.array( self.dataset[idx][2] )
                R,G,B = r.reshape(32,32), g.reshape(32,32), b.reshape(32,32)
                im_tensor = torch.zeros(3,32,32, dtype=torch.float)
                im_tensor[0,:,:] = torch.from_numpy(R)
                im_tensor[1,:,:] = torch.from_numpy(G)
                im_tensor[2,:,:] = torch.from_numpy(B)
                bb_tensor = torch.tensor(self.dataset[idx][3], dtype=torch.float)
                sample = {'image' : im_tensor, 
                          'bbox' : bb_tensor,
                          'label' : self.dataset[idx][4] }
                return sample

        def load_PurdueShapes5_dataset(self, dataserver_train, dataserver_test ):       
            self.train_dataloader = torch.utils.data.DataLoader(dataserver_train,
                               batch_size=self.dl_studio.batch_size,shuffle=True, num_workers=4)
            self.test_dataloader = torch.utils.data.DataLoader(dataserver_test,
                               batch_size=self.dl_studio.batch_size,shuffle=False, num_workers=4)
    

        class SkipBlock3(nn.Module):
            """
            Class Path:   DLStudio  ->  DetectAndLocalize  ->  SkipBlock
            """            
            def __init__(self, in_ch, out_ch, downsample=False, skip_connections=True):
                super(DLStudio.DetectAndLocalize.SkipBlock3, self).__init__()
                self.downsample = downsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convo1 = nn.Conv2d(in_ch, in_ch, 3, stride=1, padding=1)
                self.convo2 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.bn1 = nn.BatchNorm2d(in_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                self.in2out  =  nn.Conv2d(in_ch, out_ch, 1)       
                if downsample:
                    ##  Setting stride to 2 and kernel_size to 1 amounts to retaining every
                    ##  other pixel in the image --- which halves the size of the image:
                    self.downsampler1 = nn.Conv2d(in_ch, in_ch, 1, stride=2)
                    self.downsampler2 = nn.Conv2d(out_ch, out_ch, 1, stride=2)

            def forward(self, x):
                identity = x                                     
                out = self.convo1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                out = self.convo2(out)                              
                out = self.bn2(out)                              
                out = nn.functional.relu(out)
                if self.downsample:
                    identity = self.downsampler1(identity)
                    out = self.downsampler2(out)
                if self.skip_connections:
                    if (self.in_ch == self.out_ch) and (self.downsample is False):
                        out = out + identity
                    elif (self.in_ch != self.out_ch) and (self.downsample is False):
                        identity = self.in2out( identity )     
                        out = out + identity
                    elif (self.in_ch != self.out_ch) and (self.downsample is True):
                        out = out + torch.cat((identity, identity), dim=1)
                return out



        class LOADnet1(nn.Module):
            """
            The acronym 'LOAD' stands for 'LOcalization And Detection'.  LOADnet1 only
            uses fully-connected layers for the regression

            Class Path:   DLStudio  ->  DetectAndLocalize  ->  LOADnet1
            """
            def __init__(self, skip_connections=True, depth=32):
                super(DLStudio.DetectAndLocalize.LOADnet1, self).__init__()
                self.pool_count = 3
                self.depth = depth // 2
                self.conv = nn.Conv2d(3, 64, 3, padding=1)
                self.skip64 = DLStudio.DetectAndLocalize.SkipBlock3(64, 64, skip_connections=skip_connections)
                self.skip64ds = DLStudio.DetectAndLocalize.SkipBlock3(64, 64, downsample=True, skip_connections=skip_connections)
                self.skip64to128 = DLStudio.DetectAndLocalize.SkipBlock3(64, 128, skip_connections=skip_connections )
                self.skip128 = DLStudio.DetectAndLocalize.SkipBlock3(128, 128, skip_connections=skip_connections)
                self.skip128ds = DLStudio.DetectAndLocalize.SkipBlock3(128,128, downsample=True, skip_connections=skip_connections)
                self.fc1 =  nn.Linear(128 * (32 // 2**self.pool_count)**2, 1000)
                self.fc2 =  nn.Linear(1000, 5)
                self.fc3 =  nn.Linear(32768, 1000)
                self.fc4 =  nn.Linear(1000, 4)

            def forward(self, x):
                x = nn.MaxPool2d(2,2)(nn.functional.relu(self.conv(x)))          
                ## The labeling section:
                for _ in range(self.depth // 4):
                    x1 = self.skip64(x)                                               
                x1 = self.skip64ds(x1)
                for _ in range(self.depth // 4):
                    x1 = self.skip64(x1)                                               
                x1 = self.skip64to128(x1)
                for _ in range(self.depth // 4):
                    x1 = self.skip128(x1)                                               
                x1 = self.skip128ds(x1)                                               
                for _ in range(self.depth // 4):
                    x1 = self.skip128(x1)                                               
                x1  =  x.view( x1.shape[0], - 1 )
                x1 = nn.functional.relu(self.fc1(x1))
                x1 = self.fc2(x1)
                ## The Bounding Box regression:
                x2 =  x.view( x.shape[0], - 1 )
                x2 = nn.functional.relu(self.fc3(x2))
                x2 = self.fc4(x2)
                return x1,x2

        class LOADnet2(nn.Module):
            """
            The acronym 'LOAD' stands for 'LOcalization And Detection'.  LOADnet2 uses
            both convo and linear layers for regression

            Class Path:   DLStudio  ->  DetectAndLocalize  ->  LOADnet2
            """ 
            def __init__(self, skip_connections=True, depth=8):
                super(DLStudio.DetectAndLocalize.LOADnet2, self).__init__()
                if depth not in [8,10,12,14,16]:
                    sys.exit("LOADnet2 has only been tested for 'depth' values 8, 10, 12, 14, and 16")
                self.depth = depth // 2
                self.conv = nn.Conv2d(3, 64, 3, padding=1)
                self.bn1  = nn.BatchNorm2d(64)
                self.bn2  = nn.BatchNorm2d(128)
                self.skip64_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip64_arr.append(DLStudio.DetectAndLocalize.SkipBlock3(64, 64,
                                                          skip_connections=skip_connections))
                self.skip64ds = DLStudio.DetectAndLocalize.SkipBlock3(64, 64, 
                                            downsample=True, skip_connections=skip_connections)
                self.skip64to128 = DLStudio.DetectAndLocalize.SkipBlock3(64, 128, 
                                                            skip_connections=skip_connections )
                self.skip128_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip128_arr.append(DLStudio.DetectAndLocalize.SkipBlock3(128, 128,
                                                         skip_connections=skip_connections))
                self.skip128ds = DLStudio.DetectAndLocalize.SkipBlock3(128,128,
                                            downsample=True, skip_connections=skip_connections)
                self.fc1 =  nn.Linear(2048, 1000)
                self.fc2 =  nn.Linear(1000, 5)

                ##  for regression
                self.conv_seqn = nn.Sequential(
                    nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
                    nn.BatchNorm2d(64),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True)
                )
                self.fc_seqn = nn.Sequential(
                    nn.Linear(16384, 1024),
                    nn.ReLU(inplace=True),
                    nn.Linear(1024, 512),
                    nn.ReLU(inplace=True),
                    nn.Linear(512, 4)        ## output for the 4 coords (x_min,y_min,x_max,y_max) of BBox
                )

            def forward(self, x):
                x = nn.MaxPool2d(2,2)(nn.functional.relu(self.conv(x)))          
                ## The labeling section:
                x1 = x.clone()
                for i,skip64 in enumerate(self.skip64_arr[:self.depth//4]):
                    x1 = skip64(x1)                
                x1 = self.skip64ds(x1)
                for i,skip64 in enumerate(self.skip64_arr[self.depth//4:]):
                    x1 = skip64(x1)                
                x1 = self.bn1(x1)
                x1 = self.skip64to128(x1)
                for i,skip128 in enumerate(self.skip128_arr[:self.depth//4]):
                    x1 = skip128(x1)                
                x1 = self.bn2(x1)
                x1 = self.skip128ds(x1)
                for i,skip128 in enumerate(self.skip128_arr[self.depth//4:]):
                    x1 = skip128(x1)                
                x1 = x1.view( x1.shape[0], - 1 )
                x1 = nn.functional.relu(self.fc1(x1))
                x1 = self.fc2(x1)
                ## The Bounding Box regression:
                x2 = self.conv_seqn(x)
                # flatten
                x2 = x2.view( x.shape[0], - 1 )
                x2 = self.fc_seqn(x2)
                return x1,x2


        class LOADnet3(nn.Module):
            """
            The acronym 'LOAD' stands for 'LOcalization And Detection'.  LOADnet3 uses
            both convo and linear layers for regression

            Class Path:   DLStudio  ->  DetectAndLocalize  ->  LOADnet3

            """ 
            def __init__(self, skip_connections=True, depth=8):
                super(DLStudio.DetectAndLocalize.LOADnet3, self).__init__()
                if depth not in [4, 8, 16]:
                    sys.exit("LOADnet2 has been tested for 'depth' for only 4, 8, and 16")
                self.depth = depth // 4
                self.conv = nn.Conv2d(3, 64, 3, padding=1)
                self.skip64_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip64_arr.append(DLStudio.DetectAndLocalize.SkipBlock3(64, 64,
                                                          skip_connections=skip_connections))
                self.skip64ds = DLStudio.DetectAndLocalize.SkipBlock3(64, 64, 
                                            downsample=True, skip_connections=skip_connections)
                self.skip64to128 = DLStudio.DetectAndLocalize.SkipBlock3(64, 128, 
                                                            skip_connections=skip_connections )
                self.skip128_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip128_arr.append(DLStudio.DetectAndLocalize.SkipBlock3(128, 128,
                                                         skip_connections=skip_connections))
                self.skip128ds = DLStudio.DetectAndLocalize.SkipBlock3(128,128,
                                            downsample=True, skip_connections=skip_connections)
                self.fc1 =  nn.Linear(2048, 1000)
                self.fc2 =  nn.Linear(1000, 5)

                ##  for regression
                self.conv_seqn = nn.Sequential(
                    nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
                    nn.ReLU(inplace=True)
                )
                self.fc_seqn = nn.Sequential(
                    nn.Linear(16384, 1024),
                    nn.ReLU(inplace=True),
                    nn.Linear(1024, 512),
                    nn.ReLU(inplace=True),
                    nn.Linear(512, 4)
                )
            def forward(self, x):
                x = nn.MaxPool2d(2,2)(nn.functional.relu(self.conv(x)))          
                ## The labeling section:
                x1 = x.clone()
                for i,skip64 in enumerate(self.skip64_arr[:self.depth//4]):
                    x1 = skip64(x1)                
                x1 = self.skip64ds(x1)
                for i,skip64 in enumerate(self.skip64_arr[self.depth//4:]):
                    x1 = skip64(x1)                
                x1 = self.skip64ds(x1)
                x1 = self.skip64to128(x1)
                for i,skip128 in enumerate(self.skip128_arr[:self.depth//4]):
                    x1 = skip128(x1)                
                for i,skip128 in enumerate(self.skip128_arr[self.depth//4:]):
                    x1 = skip128(x1)                
                x1  =  x1.view( x1.shape[0], - 1 )
                x1 = nn.functional.relu(self.fc1(x1))
                x1 = self.fc2(x1)
                ## The Bounding Box regression:
                for _ in range(4):
                    x2 = self.skip64(x)                                               
                x2 = self.skip64to128(x2)
                for _ in range(4):
                    x2 = self.skip128(x2)                                               
                x2 = x.view( x.shape[0], - 1 )
                x2 = nn.functional.relu(self.fc3(x2))
                x2 = self.fc4(x2)
                return x1,x2


        class DIoULoss(nn.Module):
            """
            Class Path:   DLStudio  ->  DetectAndLocalize  ->  DIOULoss

            This is a Custom Loss Function for implementing the variants of the IoU 
            (Intersection over Union) loss as described on Slides 37 through 42 of my 
            Week 7 presentation on Object Detection and Localization.
            """
            def __init__(self, dl_studio, loss_mode):
                super(DLStudio.DetectAndLocalize.DIoULoss, self).__init__()
                self.dl_studio = dl_studio
                self.loss_mode = loss_mode

            def forward(self, predicted, target, loss_mode):
                debug = 0
                ##  We calculate the MSELoss between the predicted and the target BBs just for sanity check.
                ##  It is not used in the loss that is returned by this function [However, note that the 
                ##  d2_loss defined below is the same thing as what is returned by MSELoss]:
                displacement_loss = nn.MSELoss()(predicted, target)                                           
                ##  We call the MSELoss again, but this time with "reduction='none'".  The reason for that
                ##  is that we need to calculate the MSELoss on a per-instance basis in the batch for the
                ##  normalizations we are going to need later in our calculation of the IoU-based loss function.
                ##  The following call returns a tensor of shape (Bx4) where B is the batch size and 4
                ##  is for four numeric values in a BB vector.
                d2_loss_per_instance = nn.MSELoss(reduction='none')(predicted, target)                        
                ##  Averaging the above along Axis 1 gives us the instance based MSE Loss we want:
                d2_mean_loss_per_instance = torch.mean(d2_loss_per_instance, 1)                               
                ##  Averaging of the above along Axis 0 should give us a single scalar that would be
                ##  the same as the "displacement_loss" in the first line:
                d2_loss = torch.mean(d2_mean_loss_per_instance,0)                                             
                if debug:
                    print("\n\nMSE Loss: ", displacement_loss)
                    print("\n\nd2_loss_per_instance_in_batch: ", d2_loss_per_instance)
                    print("\n\nd2_mean_loss_per_instance_in_batch: ", d2_mean_loss_per_instance)
                    print("\n\nd2 loss: ", d2_loss)
  
                ##  Our next job is to figure out the BB for the convex hull of the predicted and target BBs. To 
                ##  thta end, we first find the upper-left corner of the convex hull by finding the infimum of the
                ##  of the min (i,j) coordinates associated with the predicted and the target BBs:
                hull_min_i  = torch.min( torch.cat( ( torch.transpose( torch.unsqueeze(predicted[:,0],0), 1,0 ),
                                                      torch.transpose( torch.unsqueeze(predicted[:,2],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,0],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,2],0), 1,0 ) ), 1 ), 1 )[0].type(torch.uint8)
                hull_min_j  = torch.min( torch.cat( ( torch.transpose( torch.unsqueeze(predicted[:,1],0), 1,0 ),
                                                      torch.transpose( torch.unsqueeze(predicted[:,3],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,1],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,3],0), 1,0 ) ), 1 ), 1 )[0].type(torch.uint8)

                ##  Next we need to find the lower-right corner of the convex hull.  We do so by finding the
                ##  supremum of the max (i,j) coordinates associated with the predicted and the target BBs:
                hull_max_i  = torch.max( torch.cat( ( torch.transpose( torch.unsqueeze(predicted[:,0],0), 1,0 ),
                                                      torch.transpose( torch.unsqueeze(predicted[:,2],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,0],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,2],0), 1,0 ) ), 1 ), 1 )[0].type(torch.uint8)

                hull_max_j  = torch.max( torch.cat( ( torch.transpose( torch.unsqueeze(predicted[:,1],0), 1,0 ),
                                                      torch.transpose( torch.unsqueeze(predicted[:,3],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,1],0), 1,0 ),
                                                         torch.transpose( torch.unsqueeze(target[:,3],0), 1,0 ) ), 1 ), 1 )[0].type(torch.uint8)

                ##  We now call on the torch.cat to organize the instance-based convex_hull min and max coordinates
                ##  into what the convex-hull BB should look like for a batch.  If B is the batch size, the shape of 
                ##  convex_hull_bb should be (B, 4):
                convex_hull_bb = torch.cat( ( torch.transpose( torch.unsqueeze(hull_min_i,0), 1,0), 
                                              torch.transpose( torch.unsqueeze(hull_min_j,0), 1,0), 
                                              torch.transpose( torch.unsqueeze(hull_max_i,0), 1,0), 
                                              torch.transpose( torch.unsqueeze(hull_max_j,0), 1,0) ), 1 ).float().to(self.dl_studio.device)

                ##  Need the square of the diagonal of the convex hull for normalization:
                convex_hull_diagonal_squared  =  torch.square(convex_hull_bb[:,0] - convex_hull_bb[:,2])  +  torch.square(convex_hull_bb[:,1] - convex_hull_bb[:,3])

                ##  Since we will be using the BB corners for indexing, we need to convert them into ints:
                predicted = predicted.type(torch.uint8)
                target = target.type(torch.uint8)
                convex_hull_bb = convex_hull_bb.type(torch.uint8)

                ##  Our next job is to convert all three BBs --- predicted, target, and convex_hull --- into binary
                ##  for set operations of union, intersection, and the set-difference of the union from the 
                ##  convex hull.  We start by initializing the three arras for each instance in the batch:
                img_size = self.dl_studio.image_size
                predicted_arr = torch.zeros(predicted.shape[0], img_size[0], img_size[1]).to(self.dl_studio.device)    
                target_arr = torch.zeros(predicted.shape[0], img_size[0], img_size[1]).to(self.dl_studio.device)       
                convex_hull_arr = torch.zeros(predicted.shape[0], img_size[0], img_size[1]).to(self.dl_studio.device)  
                ##  We fill the three arrays --- predicted, target, and convex_hull --- according to their respective BBs:
                for k in range(predicted_arr.shape[0]):                                                            
                    predicted_arr[ k, predicted[k,0]:predicted[k,2],  predicted[k,1]:predicted[k,3] ] = 1         
                    target_arr[ k, target[k,0]:target[k,2],  target[k,1]:target[k,3] ] = 1         
                    convex_hull_arr[ k, convex_hull_bb[k,0]:convex_hull_bb[k,2],  convex_hull_bb[k,1]:convex_hull_bb[k,3] ] = 1         
                ##  We are ready for the set operations:
                intersection_arr = predicted_arr * target_arr                                                     
                intersecs = torch.sum( intersection_arr, dim=(1,2) )                                              
                union_arr = torch.logical_or( predicted_arr > 0, target_arr > 0 ).type(torch.uint8)               
                unions = torch.sum( union_arr, dim=(1,2) )                                                        
                ## find the set difference of the convex hull and the union for each batch instance:
                diff_arr = (convex_hull_arr !=  union_arr).type(torch.uint8)
                ## what's the total number of pixels in the the set difference:            
                diff_sum_per_instance = torch.sum( diff_arr, dim=(1,2) )
                ## also, what is the total number of pixels in the convex hull for each batch instance:
                convex_hull_sum_per_instance = torch.sum( convex_hull_arr, dim=(1,2) )
                if  (convex_hull_sum_per_instance < 10).any(): return torch.tensor([float('nan')])
                ## find the ratio we need for the DIoU formula [see Eq. (8) on Slide 40 of my Week 7 slides]:
                epsilon = 1e-6
                ratio = diff_sum_per_instance.type(torch.float) / (convex_hull_sum_per_instance.type(torch.float) + epsilon) 
                ## find the IoU            
                iou = intersecs / (unions + epsilon)                          
                iou_loss = torch.mean(1 - iou, 0)                             
                d2_normed = d2_mean_loss_per_instance / (convex_hull_diagonal_squared + epsilon)     
                d2_normed_loss = torch.mean(d2_normed, 0)        
                ratio_loss  =  torch.mean( ratio, 0 )
                if self.loss_mode == 'd2':
                    diou_loss =  d2_loss                         
                elif self.loss_mode == 'diou1':
                    diou_loss = iou_loss + d2_loss               
                elif self.loss_mode == 'diou2':
                    diou_loss = iou_loss + d2_normed_loss        
                elif self.loss_mode == 'diou3':
                    diou_loss = iou_loss + d2_normed_loss + ratio_loss
                return diou_loss



        def run_code_for_training_with_iou_regression(self, net, loss_mode='d2', show_images=True):
            """
            This training routine is called by

                     object_detection_and_localization_iou.py

            in the Examples directory.

            The possible values for loss_mode are:  'd2', 'diou1', 'diou2', 'diou3' with the following meanings:

            d2     :   d2_loss                                         This is just the MSE loss based on the square
                                                                       of the distance between the centers of the 
                                                                       predicted BB and the ground-truth BB.

            diou1  :   iou_loss   +   d2_loss                          We add to the pure IOU loss the value d2_loss
                                                                       defined above
          
            diou2  :   iou_loss   +   d2_normed_loss                   We now normalize the squared distance between the
                                                                       centers of the predicted BB and ground_truth BB by
                                                                       the diagonal of the convex hull of the two BBs.

            diou3  :   iou_loss   +   d2_normed_loss + ratio_loss      We now normalize the 


            IMPORTANT NOTE:  You are likely to get the best results if you set the learning rate to 1e-4 for d2 and 
                             diou1 options.  If the option you use is diou2 or diou3, set the learning rate to 5e-3
            """
            filename_for_out1 = "performance_numbers_" + str(self.dl_studio.epochs) + "label.txt"
            filename_for_out2 = "performance_numbers_" + str(self.dl_studio.epochs) + "regres.txt"
            FILE1 = open(filename_for_out1, 'w')
            FILE2 = open(filename_for_out2, 'w')
            net = copy.deepcopy(net)
            net = net.to(self.dl_studio.device)
            criterion1 = nn.CrossEntropyLoss()
            criterion2 = self.dl_studio.DetectAndLocalize.DIoULoss(self.dl_studio, loss_mode)
            optimizer = optim.SGD(net.parameters(), lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            print("\n\nStarting training loop...\n\n")
            start_time = time.perf_counter()
            labeling_loss_tally = []   
            regression_loss_tally = [] 
            elapsed_time = 0.0   
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss_labeling = 0.0
                running_loss_regression = 0.0       
                for i, data in enumerate(self.train_dataloader):
                    gt_too_small = False
                    inputs, bbox_gt, labels = data['image'], data['bbox'], data['label']
                    inputs = inputs.to(self.dl_studio.device)
                    labels = labels.to(self.dl_studio.device)
                    bbox_gt = bbox_gt.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    if self.debug:
                        self.dl_studio.display_tensor_as_image(
                          torchvision.utils.make_grid(inputs.cpu(), nrow=4, normalize=True, padding=2, pad_value=10))
                    outputs = net(inputs)
                    outputs_label = outputs[0]
                    bbox_pred = outputs[1]
                    if i % 500 == 499:
                        current_time = time.perf_counter()
                        elapsed_time = current_time - start_time
                        print("\n\n\n[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]      Ground Truth:     " % 
                                 (epoch+1, self.dl_studio.epochs, i+1, elapsed_time) 
                               + ' '.join('%10s' % self.dataserver_train.class_labels[labels[j].item()] 
                                                                for j in range(self.dl_studio.batch_size)))
                        inputs_copy = inputs.detach().clone()
                        inputs_copy = inputs_copy.cpu()
                        bbox_pc = bbox_pred.detach().clone()
                        bbox_pc[bbox_pc<0] = 0
                        bbox_pc[bbox_pc>31] = 31
                        bbox_pc[torch.isnan(bbox_pc)] = 0
                        _, predicted = torch.max(outputs_label.data, 1)
                        print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]  Predicted Labels:     " % 
                                (epoch+1, self.dl_studio.epochs, i+1, elapsed_time)  
                              + ' '.join('%10s' % self.dataserver_train.class_labels[predicted[j].item()] 
                                                                 for j in range(self.dl_studio.batch_size)))
                        if show_images == True:
                            for idx in range(self.dl_studio.batch_size):
                                i1 = int(bbox_gt[idx][1])
                                i2 = int(bbox_gt[idx][3])
                                j1 = int(bbox_gt[idx][0])
                                j2 = int(bbox_gt[idx][2])
                                k1 = int(bbox_pc[idx][1])
                                k2 = int(bbox_pc[idx][3])
                                l1 = int(bbox_pc[idx][0])
                                l2 = int(bbox_pc[idx][2])
                                print("                    gt_bb:  [%d,%d,%d,%d]"%(i1,j1,i2,j2))        
                                print("                  pred_bb:  [%d,%d,%d,%d]"%(k1,l1,k2,l2))
                                inputs_copy[idx,1,i1:i2,j1] = 255
                                inputs_copy[idx,1,i1:i2,j2] = 255
                                inputs_copy[idx,1,i1,j1:j2] = 255
                                inputs_copy[idx,1,i2,j1:j2] = 255
                                inputs_copy[idx,0,k1:k2,l1] = 255                      
                                inputs_copy[idx,0,k1:k2,l2] = 255
                                inputs_copy[idx,0,k1,l1:l2] = 255
                                inputs_copy[idx,0,k2,l1:l2] = 255
    
                    loss_labeling = criterion1(outputs_label, labels)
                    loss_labeling.backward(retain_graph=True)        
                    loss_regression = criterion2(bbox_pred, bbox_gt, loss_mode)
                    if torch.isnan(loss_regression): continue
                    loss_regression.backward()
                    optimizer.step()
                    running_loss_labeling += loss_labeling.item()    
                    running_loss_regression += loss_regression.item()                
                    if i % 500 == 499:    
                        avg_loss_labeling = running_loss_labeling / float(500)
                        avg_loss_regression = running_loss_regression / float(500)
                        labeling_loss_tally.append(avg_loss_labeling)  
                        regression_loss_tally.append(avg_loss_regression)    
                        print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]       loss_labeling %.3f        loss_regression: %.3f " %  (epoch+1, self.dl_studio.epochs, i+1, elapsed_time, avg_loss_labeling, avg_loss_regression))
                        FILE1.write("%.3f\n" % avg_loss_labeling)
                        FILE1.flush()
                        FILE2.write("%.3f\n" % avg_loss_regression)
                        FILE2.flush()
                        running_loss_labeling = 0.0
                        running_loss_regression = 0.0

                    if show_images == True:
                        if i%500==499:
                            logger = logging.getLogger()
                            old_level = logger.level
                            logger.setLevel(100)
                            plt.figure(figsize=[8,3])
                            plt.imshow(np.transpose(torchvision.utils.make_grid(inputs_copy, normalize=True,
                                                                             padding=3, pad_value=255).cpu(), (1,2,0)))
                            plt.show()
                            logger.setLevel(old_level)
            print("\nFinished Training\n")
            self.save_model(net)
            plt.figure(figsize=(10,5))
            plt.title("Labeling Loss vs. Iterations")
            plt.plot(labeling_loss_tally)
            plt.xlabel("iterations")
            plt.ylabel("labeling loss")
#            plt.legend()
            plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
            plt.savefig("labeling_loss.png")
            plt.show()
            plt.title("regression Loss vs. Iterations")
            plt.plot(regression_loss_tally)
            plt.xlabel("iterations")
            plt.ylabel("regression loss")
#            plt.legend()
            plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
            plt.savefig("regression_loss.png")
            plt.show()



        def run_code_for_training_with_CrossEntropy_and_MSE_Losses(self, net, show_images=True):        
            """
            This training routine is called by

                     object_detection_and_localization.py

            in the Examples directory.
            """
            filename_for_out1 = "performance_numbers_" + str(self.dl_studio.epochs) + "label.txt"
            filename_for_out2 = "performance_numbers_" + str(self.dl_studio.epochs) + "regres.txt"
            FILE1 = open(filename_for_out1, 'w')
            FILE2 = open(filename_for_out2, 'w')
            net = copy.deepcopy(net)
            net = net.to(self.dl_studio.device)
            criterion1 = nn.CrossEntropyLoss()
            criterion2 = nn.MSELoss()
            optimizer = optim.SGD(net.parameters(), lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            print("\n\nStarting training loop...\n\n")
            start_time = time.perf_counter()
            labeling_loss_tally = []   
            regression_loss_tally = [] 
            elapsed_time = 0.0   
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss_labeling = 0.0
                running_loss_regression = 0.0       
                for i, data in enumerate(self.train_dataloader):
                    gt_too_small = False
                    inputs, bbox_gt, labels = data['image'], data['bbox'], data['label']
                    if i % 500 == 499:
                        current_time = time.perf_counter()
                        elapsed_time = current_time - start_time
                        print("\n\n\n[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]      Ground Truth:     " % 
                                 (epoch+1, self.dl_studio.epochs, i+1, elapsed_time) 
                               + ' '.join('%10s' % self.dataserver_train.class_labels[labels[j].item()] 
                                                                for j in range(self.dl_studio.batch_size)))
                    inputs = inputs.to(self.dl_studio.device)
                    labels = labels.to(self.dl_studio.device)
                    bbox_gt = bbox_gt.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    if self.debug:
                        self.dl_studio.display_tensor_as_image(
                          torchvision.utils.make_grid(inputs.cpu(), nrow=4, normalize=True, padding=2, pad_value=10))
                    outputs = net(inputs)
                    outputs_label = outputs[0]
                    bbox_pred = outputs[1]
                    if i % 500 == 499:
                        inputs_copy = inputs.detach().clone()
                        inputs_copy = inputs_copy.cpu()
                        bbox_pc = bbox_pred.detach().clone()
                        bbox_pc[bbox_pc<0] = 0
                        bbox_pc[bbox_pc>31] = 31
                        bbox_pc[torch.isnan(bbox_pc)] = 0
                        _, predicted = torch.max(outputs_label.data, 1)
                        print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]  Predicted Labels:     " % 
                                (epoch+1, self.dl_studio.epochs, i+1, elapsed_time)  
                              + ' '.join('%10s' % self.dataserver_train.class_labels[predicted[j].item()] 
                                                                 for j in range(self.dl_studio.batch_size)))
                        for idx in range(self.dl_studio.batch_size):
                            i1 = int(bbox_gt[idx][1])
                            i2 = int(bbox_gt[idx][3])
                            j1 = int(bbox_gt[idx][0])
                            j2 = int(bbox_gt[idx][2])
                            k1 = int(bbox_pc[idx][1])
                            k2 = int(bbox_pc[idx][3])
                            l1 = int(bbox_pc[idx][0])
                            l2 = int(bbox_pc[idx][2])
                            print("                    gt_bb:  [%d,%d,%d,%d]"%(i1,j1,i2,j2))
                            print("                  pred_bb:  [%d,%d,%d,%d]"%(k1,l1,k2,l2))
                            inputs_copy[idx,1,i1:i2,j1] = 255
                            inputs_copy[idx,1,i1:i2,j2] = 255
                            inputs_copy[idx,1,i1,j1:j2] = 255
                            inputs_copy[idx,1,i2,j1:j2] = 255
                            inputs_copy[idx,0,k1:k2,l1] = 255                      
                            inputs_copy[idx,0,k1:k2,l2] = 255
                            inputs_copy[idx,0,k1,l1:l2] = 255
                            inputs_copy[idx,0,k2,l1:l2] = 255
                    loss_labeling = criterion1(outputs_label, labels)
                    loss_labeling.backward(retain_graph=True)        
                    loss_regression = criterion2(bbox_pred, bbox_gt)
                    loss_regression.backward()
                    optimizer.step()
                    running_loss_labeling += loss_labeling.item()    
                    running_loss_regression += loss_regression.item()                
                    if i % 500 == 499:    
                        avg_loss_labeling = running_loss_labeling / float(500)
                        avg_loss_regression = running_loss_regression / float(500)
                        labeling_loss_tally.append(avg_loss_labeling)  
                        regression_loss_tally.append(avg_loss_regression)    
                        print("[epoch:%d/%d  iter=%4d  elapsed_time=%5d secs]       loss_labeling %.3f        loss_regression: %.3f " %  (epoch+1, self.dl_studio.epochs, i+1, elapsed_time, avg_loss_labeling, avg_loss_regression))
                        FILE1.write("%.3f\n" % avg_loss_labeling)
                        FILE1.flush()
                        FILE2.write("%.3f\n" % avg_loss_regression)
                        FILE2.flush()
                        running_loss_labeling = 0.0
                        running_loss_regression = 0.0
#                    if i%500==499:
                    if i%500==499 and show_images is True:
                        logger = logging.getLogger()
                        old_level = logger.level
                        logger.setLevel(100)
                        plt.figure(figsize=[8,3])
                        plt.imshow(np.transpose(torchvision.utils.make_grid(inputs_copy, normalize=True,
                                                                         padding=3, pad_value=255).cpu(), (1,2,0)))
                        plt.show()
                        logger.setLevel(old_level)
            print("\nFinished Training\n")
            self.save_model(net)
            plt.figure(figsize=(10,5))
            plt.title("Labeling Loss vs. Iterations")
            plt.plot(labeling_loss_tally)
            plt.xlabel("iterations")
            plt.ylabel("labeling loss")
#            plt.legend()
            plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
            plt.savefig("labeling_loss.png")
            plt.show()
            plt.title("regression Loss vs. Iterations")
            plt.plot(regression_loss_tally)
            plt.xlabel("iterations")
            plt.ylabel("regression loss")
#            plt.legend()
            plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
            plt.savefig("regression_loss.png")
            plt.show()


        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)


        def run_code_for_testing_detection_and_localization(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            correct = 0
            total = 0
            confusion_matrix = torch.zeros(len(self.dataserver_train.class_labels), 
                                           len(self.dataserver_train.class_labels))
            class_correct = [0] * len(self.dataserver_train.class_labels)
            class_total = [0] * len(self.dataserver_train.class_labels)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    images, bounding_box, labels = data['image'], data['bbox'], data['label']
                    labels = labels.tolist()
                    if self.dl_studio.debug_test and i % 50 == 0:
                        print("\n\n[i=%d:] Ground Truth:     " %i + ' '.join('%10s' % 
                         self.dataserver_train.class_labels[labels[j]] for j in range(self.dl_studio.batch_size)))
                    outputs = net(images)
                    outputs_label = outputs[0]
                    outputs_regression = outputs[1]
                    outputs_regression[outputs_regression < 0] = 0
                    outputs_regression[outputs_regression > 31] = 31
                    outputs_regression[torch.isnan(outputs_regression)] = 0
                    output_bb = outputs_regression.tolist()
                    _, predicted = torch.max(outputs_label.data, 1)
                    predicted = predicted.tolist()
                    if self.dl_studio.debug_test and i % 50 == 0:
                        print("[i=%d:] Predicted Labels: " %i + ' '.join('%10s' % 
                              self.dataserver_train.class_labels[predicted[j]] for j in range(self.dl_studio.batch_size)))
                        for idx in range(self.dl_studio.batch_size):
                            i1 = int(bounding_box[idx][1])
                            i2 = int(bounding_box[idx][3])
                            j1 = int(bounding_box[idx][0])
                            j2 = int(bounding_box[idx][2])
                            k1 = int(output_bb[idx][1])
                            k2 = int(output_bb[idx][3])
                            l1 = int(output_bb[idx][0])
                            l2 = int(output_bb[idx][2])
                            print("                    gt_bb:  [%d,%d,%d,%d]"%(j1,i1,j2,i2))
                            print("                  pred_bb:  [%d,%d,%d,%d]"%(l1,k1,l2,k2))
                            images[idx,0,i1:i2,j1] = 255
                            images[idx,0,i1:i2,j2] = 255
                            images[idx,0,i1,j1:j2] = 255
                            images[idx,0,i2,j1:j2] = 255
                            images[idx,2,k1:k2,l1] = 255                      
                            images[idx,2,k1:k2,l2] = 255
                            images[idx,2,k1,l1:l2] = 255
                            images[idx,2,k2,l1:l2] = 255
                        logger = logging.getLogger()
                        old_level = logger.level
                        logger.setLevel(100)
                        plt.figure(figsize=[8,3])
                        plt.imshow(np.transpose(torchvision.utils.make_grid(images, normalize=True,
                                                                         padding=3, pad_value=255).cpu(), (1,2,0)))
                        plt.show()
                        logger.setLevel(old_level)
                    for label,prediction in zip(labels,predicted):
                        confusion_matrix[label][prediction] += 1
                    total += len(labels)
                    correct +=  [predicted[ele] == labels[ele] for ele in range(len(predicted))].count(True)
                    comp = [predicted[ele] == labels[ele] for ele in range(len(predicted))]
                    for j in range(self.dl_studio.batch_size):
                        label = labels[j]
                        class_correct[label] += comp[j]
                        class_total[label] += 1
            print("\n")
            for j in range(len(self.dataserver_train.class_labels)):
                print('Prediction accuracy for %5s : %2d %%' % (
              self.dataserver_train.class_labels[j], 100 * class_correct[j] / class_total[j]))
            print("\n\n\nOverall accuracy of the network on the 1000 test images: %d %%" % 
                                                                   (100 * correct / float(total)))
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                "
            for j in range(len(self.dataserver_train.class_labels)):  
                                 out_str +=  "%15s" % self.dataserver_train.class_labels[j]   
            print(out_str + "\n")
            for i,label in enumerate(self.dataserver_train.class_labels):
                out_percents = [100 * confusion_matrix[i,j] / float(class_total[i]) 
                                 for j in range(len(self.dataserver_train.class_labels))]
                out_percents = ["%.2f" % item.item() for item in out_percents]
                out_str = "%12s:  " % self.dataserver_train.class_labels[i]
                for j in range(len(self.dataserver_train.class_labels)): 
                                                       out_str +=  "%15s" % out_percents[j]
                print(out_str)



    ###%%%
    #####################################################################################################################
    #################################  Start Definition of Inner Class SemanticSegmentation  ############################

    class SemanticSegmentation(nn.Module):             
        """
        The purpose of this inner class is to be able to use the DLStudio platform for
        experiments with semantic segmentation.  At its simplest level, the purpose of
        semantic segmentation is to assign correct labels to the different objects in a
        scene, while localizing them at the same time.  At a more sophisticated level, a
        system that carries out semantic segmentation should also output a symbolic
        expression based on the objects found in the image and their spatial relationships
        with one another.

        The workhorse of this inner class is the mUNet network that is based on the UNET
        network that was first proposed by Ronneberger, Fischer and Brox in the paper
        "U-Net: Convolutional Networks for Biomedical Image Segmentation".  Their Unet
        extracts binary masks for the cell pixel blobs of interest in biomedical images.
        The output of their Unet can therefore be treated as a pixel-wise binary classifier
        at each pixel position.  The mUnet class, on the other hand, is intended for
        segmenting out multiple objects simultaneously form an image. [A weaker reason for
        "Multi" in the name of the class is that it uses skip connections not only across
        the two arms of the "U", but also also along the arms.  The skip connections in the
        original Unet are only between the two arms of the U.  In mUnet, each object type is
        assigned a separate channel in the output of the network.

        This version of DLStudio also comes with a new dataset, PurdueShapes5MultiObject,
        for experimenting with mUnet.  Each image in this dataset contains a random number
        of selections from five different shapes, with the shapes being randomly scaled,
        oriented, and located in each image.  The five different shapes are: rectangle,
        triangle, disk, oval, and star.

           Class Path:   DLStudio  ->  SemanticSegmentation
        """
        def __init__(self, dl_studio, max_num_objects, dataserver_train=None, dataserver_test=None, dataset_file_train=None, dataset_file_test=None):
            super(DLStudio.SemanticSegmentation, self).__init__()
            self.dl_studio = dl_studio
            self.max_num_objects = max_num_objects
            self.dataserver_train = dataserver_train
            self.dataserver_test = dataserver_test


        class PurdueShapes5MultiObjectDataset(torch.utils.data.Dataset):
            """
            The very first thing to note is that the images in the dataset
            PurdueShapes5MultiObjectDataset are of size 64x64.  Each image has a random
            number (up to five) of the objects drawn from the following five shapes:
            rectangle, triangle, disk, oval, and star.  Each shape is randomized with
            respect to all its parameters, including those for its scale and location in the
            image.

            Each image in the dataset is represented by two data objects, one a list and the
            other a dictionary. The list data objects consists of the following items:

                [R, G, B, mask_array, mask_val_to_bbox_map]                                   ## (A)
            
            and the other data object is a dictionary that is set to:
            
                label_map = {'rectangle':50, 
                             'triangle' :100, 
                             'disk'     :150, 
                             'oval'     :200, 
                             'star'     :250}                                                 ## (B)
            
            Note that that second data object for each image is the same, as shown above.

            In the rest of this comment block, I'll explain in greater detail the elements
            of the list in line (A) above.

            
            R,G,B:
            ------

            Each of these is a 4096-element array whose elements store the corresponding
            color values at each of the 4096 pixels in a 64x64 image.  That is, R is a list
            of 4096 integers, each between 0 and 255, for the value of the red component of
            the color at each pixel. Similarly, for G and B.
            

            mask_array:
            ----------

            The fourth item in the list shown in line (A) above is for the mask which is a
            numpy array of shape:
            
                           (5, 64, 64)
            
            It is initialized by the command:
            
                 mask_array = np.zeros((5,64,64), dtype=np.uint8)
            
            In essence, the mask_array consists of five planes, each of size 64x64.  Each
            plane of the mask array represents an object type according to the following
            shape_index
            
                    shape_index = (label_map[shape] - 50) // 50
            
            where the label_map is as shown in line (B) above.  In other words, the
            shape_index values for the different shapes are:
            
                     rectangle:  0
                      triangle:  1
                          disk:  2
                          oval:  3
                          star:  4
            
            Therefore, the first layer (of index 0) of the mask is where the pixel values of
            50 are stored at all those pixels that belong to the rectangle shapes.
            Similarly, the second mask layer (of index 1) is where the pixel values of 100
            are stored at all those pixel coordinates that belong to the triangle shapes in
            an image; and so on.
            
            It is in the manner described above that we define five different masks for an
            image in the dataset.  Each mask is for a different shape and the pixel values
            at the nonzero pixels in each mask layer are keyed to the shapes also.
            
            A reader is likely to wonder as to the need for this redundancy in the dataset
            representation of the shapes in each image.  Such a reader is likely to ask: Why
            can't we just use the binary values 1s and 0s in each mask layer where the
            corresponding pixels are in the image?  Setting these mask values to 50, 100,
            etc., was done merely for convenience.  I went with the intuition that the
            learning needed for multi-object segmentation would become easier if each shape
            was represented by a different pixels value in the corresponding mask. So I went
            ahead incorporated that in the dataset generation program itself.

            The mask values for the shapes are not to be confused with the actual RGB values
            of the pixels that belong to the shapes. The RGB values at the pixels in a shape
            are randomly generated.  Yes, all the pixels in a shape instance in an image
            have the same RGB values (but that value has nothing to do with the values given
            to the mask pixels for that shape).
            
            
            mask_val_to_bbox_map:
            --------------------
                   
            The fifth item in the list in line (A) above is a dictionary that tells us what
            bounding-box rectangle to associate with each shape in the image.  To illustrate
            what this dictionary looks like, assume that an image contains only one
            rectangle and only one disk, the dictionary in this case will look like:
            
                mask values to bbox mappings:  {200: [], 
                                                250: [], 
                                                100: [], 
                                                 50: [[56, 20, 63, 25]], 
                                                150: [[37, 41, 55, 59]]}
            
            Should there happen to be two rectangles in the same image, the dictionary would
            then be like:
            
                mask values to bbox mappings:  {200: [], 
                                                250: [], 
                                                100: [], 
                                                 50: [[56, 20, 63, 25], [18, 16, 32, 36]], 
                                                150: [[37, 41, 55, 59]]}
            
            Therefore, it is not a problem even if all the objects in an image are of the
            same type.  Remember, the object that are selected for an image are shown
            randomly from the different shapes.  By the way, an entry like '[56, 20, 63,
            25]' for the bounding box means that the upper-left corner of the BBox for the
            'rectangle' shape is at (56,20) and the lower-right corner of the same is at the
            pixel coordinates (63,25).
            
            As far as the BBox quadruples are concerned, in the definition
            
                    [min_x,min_y,max_x,max_y]
            
            note that x is the horizontal coordinate, increasing to the right on your
            screen, and y is the vertical coordinate increasing downwards.

            Class Path:   DLStudio  ->  SemanticSegmentation  ->  PurdueShapes5MultiObjectDataset

            """
            def __init__(self, dl_studio, segmenter, train_or_test, dataset_file):
                super(DLStudio.SemanticSegmentation.PurdueShapes5MultiObjectDataset, self).__init__()
                max_num_objects = segmenter.max_num_objects
                if train_or_test == 'train' and dataset_file == "PurdueShapes5MultiObject-10000-train.gz":
                    if os.path.exists("torch_saved_PurdueShapes5MultiObject-10000_dataset.pt") and \
                              os.path.exists("torch_saved_PurdueShapes5MultiObject_label_map.pt"):
                        print("\nLoading training data from torch saved file")
                        self.dataset = torch.load("torch_saved_PurdueShapes5MultiObject-10000_dataset.pt")
                        self.label_map = torch.load("torch_saved_PurdueShapes5MultiObject_label_map.pt")
                        self.num_shapes = len(self.label_map)
                        self.image_size = dl_studio.image_size
                    else: 
                        print("""\n\n\nLooks like this is the first time you will be loading in\n"""
                              """the dataset for this script. First time loading could take\n"""
                              """a few minutes.  Any subsequent attempts will only take\n"""
                              """a few seconds.\n\n\n""")
                        root_dir = dl_studio.dataroot
                        f = gzip.open(root_dir + dataset_file, 'rb')
                        dataset = f.read()
                        self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                        torch.save(self.dataset, "torch_saved_PurdueShapes5MultiObject-10000_dataset.pt")
                        torch.save(self.label_map, "torch_saved_PurdueShapes5MultiObject_label_map.pt")
                        # reverse the key-value pairs in the label dictionary:
                        self.class_labels = dict(map(reversed, self.label_map.items()))
                        self.num_shapes = len(self.class_labels)
                        self.image_size = dl_studio.image_size
                else:
                    root_dir = dl_studio.dataroot
                    f = gzip.open(root_dir + dataset_file, 'rb')
                    dataset = f.read()
                    if sys.version_info[0] == 3:
                        self.dataset, self.label_map = pickle.loads(dataset, encoding='latin1')
                    else:
                        self.dataset, self.label_map = pickle.loads(dataset)
                    # reverse the key-value pairs in the label dictionary:
                    self.class_labels = dict(map(reversed, self.label_map.items()))
                    self.num_shapes = len(self.class_labels)
                    self.image_size = dl_studio.image_size

            def __len__(self):
                return len(self.dataset)

            def __getitem__(self, idx):
                image_size = self.image_size
                r = np.array( self.dataset[idx][0] )
                g = np.array( self.dataset[idx][1] )
                b = np.array( self.dataset[idx][2] )
                R,G,B = r.reshape(image_size[0],image_size[1]), g.reshape(image_size[0],image_size[1]), b.reshape(image_size[0],image_size[1])
                im_tensor = torch.zeros(3,image_size[0],image_size[1], dtype=torch.float)
                im_tensor[0,:,:] = torch.from_numpy(R)
                im_tensor[1,:,:] = torch.from_numpy(G)
                im_tensor[2,:,:] = torch.from_numpy(B)
                mask_array = np.array(self.dataset[idx][3])
                max_num_objects = len( mask_array[0] ) 
                mask_tensor = torch.from_numpy(mask_array)
                mask_val_to_bbox_map =  self.dataset[idx][4]
                max_bboxes_per_entry_in_map = max([ len(mask_val_to_bbox_map[key]) for key in mask_val_to_bbox_map ])
                ##  The first arg 5 is for the number of bboxes we are going to need. If all the
                ##  shapes are exactly the same, you are going to need five different bbox'es.
                ##  The second arg is the index reserved for each shape in a single bbox
                bbox_tensor = torch.zeros(max_num_objects,self.num_shapes,4, dtype=torch.float)
                for bbox_idx in range(max_bboxes_per_entry_in_map):
                    for key in mask_val_to_bbox_map:
                        if len(mask_val_to_bbox_map[key]) == 1:
                            if bbox_idx == 0:
                                bbox_tensor[bbox_idx,key,:] = torch.from_numpy(np.array(mask_val_to_bbox_map[key][bbox_idx]))
                        elif len(mask_val_to_bbox_map[key]) > 1 and bbox_idx < len(mask_val_to_bbox_map[key]):
                            bbox_tensor[bbox_idx,key,:] = torch.from_numpy(np.array(mask_val_to_bbox_map[key][bbox_idx]))
                sample = {'image'        : im_tensor, 
                          'mask_tensor'  : mask_tensor,
                          'bbox_tensor'  : bbox_tensor }
                return sample

        def load_PurdueShapes5MultiObject_dataset(self, dataserver_train, dataserver_test ):   
            self.train_dataloader = torch.utils.data.DataLoader(dataserver_train,
                        batch_size=self.dl_studio.batch_size,shuffle=True, num_workers=4)
            self.test_dataloader = torch.utils.data.DataLoader(dataserver_test,
                               batch_size=self.dl_studio.batch_size,shuffle=False, num_workers=4)


        class SkipBlockDN(nn.Module):
            """
            This class for the skip connections in the downward leg of the "U"

            Class Path:   DLStudio  ->  SemanticSegmentation  ->  SkipBlockDN
            """
            def __init__(self, in_ch, out_ch, downsample=False, skip_connections=True):
                super(DLStudio.SemanticSegmentation.SkipBlockDN, self).__init__()
                self.downsample = downsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convo1 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.convo2 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.bn1 = nn.BatchNorm2d(out_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                if downsample:
                    self.downsampler = nn.Conv2d(in_ch, out_ch, 1, stride=2)
            def forward(self, x):
                identity = x                                     
                out = self.convo1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                if self.in_ch == self.out_ch:
                    out = self.convo2(out)                              
                    out = self.bn2(out)                              
                    out = nn.functional.relu(out)
                if self.downsample:
                    out = self.downsampler(out)
                    identity = self.downsampler(identity)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity
                    else:
                        out = out + torch.cat((identity, identity), dim=1) 
                return out


        class SkipBlockUP(nn.Module):
            """
            This class is for the skip connections in the upward leg of the "U"

            Class Path:   DLStudio  ->  SemanticSegmentation  ->  SkipBlockUP
            """
            def __init__(self, in_ch, out_ch, upsample=False, skip_connections=True):
                super(DLStudio.SemanticSegmentation.SkipBlockUP, self).__init__()
                self.upsample = upsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convoT1 = nn.ConvTranspose2d(in_ch, out_ch, 3, padding=1)
                self.convoT2 = nn.ConvTranspose2d(in_ch, out_ch, 3, padding=1)
                self.bn1 = nn.BatchNorm2d(out_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                if upsample:
                    self.upsampler = nn.ConvTranspose2d(in_ch, out_ch, 1, stride=2, dilation=2, output_padding=1, padding=0)
            def forward(self, x):
                identity = x                                     
                out = self.convoT1(x)                              
                out = self.bn1(out)                              
                out = nn.functional.relu(out)
                out  =  nn.ReLU(inplace=False)(out)            
                if self.in_ch == self.out_ch:
                    out = self.convoT2(out)                              
                    out = self.bn2(out)                              
                    out = nn.functional.relu(out)
                if self.upsample:
                    out = self.upsampler(out)
                    identity = self.upsampler(identity)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity                              
                    else:
                        out = out + identity[:,self.out_ch:,:,:]
                return out
        

        class mUNet(nn.Module):
            """
            This network is called mUNet because it is intended for segmenting out
            multiple objects simultaneously form an image. [A weaker reason for "Multi" in
            the name of the class is that it uses skip connections not only across the two
            arms of the "U", but also also along the arms.]  The classic UNET was first
            proposed by Ronneberger, Fischer and Brox in the paper "U-Net: Convolutional
            Networks for Biomedical Image Segmentation".  Their UNET extracts binary masks
            for the cell pixel blobs of interest in biomedical images.  The output of their
            UNET therefore can therefore be treated as a pixel-wise binary classifier at
            each pixel position.

            The mUNet presented here, on the other hand, is meant specifically for
            simultaneously identifying and localizing multiple objects in a given image.
            Each object type is assigned a separate channel in the output of the network.

            I have created a dataset, PurdueShapes5MultiObject, for experimenting with
            mUNet.  Each image in this dataset contains a random number of selections from
            five different shapes, with the shapes being randomly scaled, oriented, and
            located in each image.  The five different shapes are: rectangle, triangle,
            disk, oval, and star.

            Class Path:   DLStudio  ->  SemanticSegmentation  ->  mUNet

            """ 
            def __init__(self, skip_connections=True, depth=16):
                super(DLStudio.SemanticSegmentation.mUNet, self).__init__()
                self.depth = depth // 2
                self.conv_in = nn.Conv2d(3, 64, 3, padding=1)
                ##  For the DN arm of the U:
                self.bn1DN  = nn.BatchNorm2d(64)
                self.bn2DN  = nn.BatchNorm2d(128)
                self.skip64DN_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip64DN_arr.append(DLStudio.SemanticSegmentation.SkipBlockDN(64, 64, skip_connections=skip_connections))
                self.skip64dsDN = DLStudio.SemanticSegmentation.SkipBlockDN(64, 64,   downsample=True, skip_connections=skip_connections)
                self.skip64to128DN = DLStudio.SemanticSegmentation.SkipBlockDN(64, 128, skip_connections=skip_connections )
                self.skip128DN_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip128DN_arr.append(DLStudio.SemanticSegmentation.SkipBlockDN(128, 128, skip_connections=skip_connections))
                self.skip128dsDN = DLStudio.SemanticSegmentation.SkipBlockDN(128,128, downsample=True, skip_connections=skip_connections)
                ##  For the UP arm of the U:
                self.bn1UP  = nn.BatchNorm2d(128)
                self.bn2UP  = nn.BatchNorm2d(64)
                self.skip64UP_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip64UP_arr.append(DLStudio.SemanticSegmentation.SkipBlockUP(64, 64, skip_connections=skip_connections))
                self.skip64usUP = DLStudio.SemanticSegmentation.SkipBlockUP(64, 64, upsample=True, skip_connections=skip_connections)
                self.skip128to64UP = DLStudio.SemanticSegmentation.SkipBlockUP(128, 64, skip_connections=skip_connections )
                self.skip128UP_arr = nn.ModuleList()
                for i in range(self.depth):
                    self.skip128UP_arr.append(DLStudio.SemanticSegmentation.SkipBlockUP(128, 128, skip_connections=skip_connections))
                self.skip128usUP = DLStudio.SemanticSegmentation.SkipBlockUP(128,128, upsample=True, skip_connections=skip_connections)
                self.conv_out = nn.ConvTranspose2d(64, 5, 3, stride=2,dilation=2,output_padding=1,padding=2)

            def forward(self, x):
                ##  Going down to the bottom of the U:
                x = nn.MaxPool2d(2,2)(nn.functional.relu(self.conv_in(x)))          
                for i,skip64 in enumerate(self.skip64DN_arr[:self.depth//4]):
                    x = skip64(x)                
        
                num_channels_to_save1 = x.shape[1] // 2
                save_for_upside_1 = x[:,:num_channels_to_save1,:,:].clone()
                x = self.skip64dsDN(x)
                for i,skip64 in enumerate(self.skip64DN_arr[self.depth//4:]):
                    x = skip64(x)                
                x = self.bn1DN(x)
                num_channels_to_save2 = x.shape[1] // 2
                save_for_upside_2 = x[:,:num_channels_to_save2,:,:].clone()
                x = self.skip64to128DN(x)
                for i,skip128 in enumerate(self.skip128DN_arr[:self.depth//4]):
                    x = skip128(x)                
        
                x = self.bn2DN(x)
                num_channels_to_save3 = x.shape[1] // 2
                save_for_upside_3 = x[:,:num_channels_to_save3,:,:].clone()
                for i,skip128 in enumerate(self.skip128DN_arr[self.depth//4:]):
                    x = skip128(x)                
                x = self.skip128dsDN(x)
                ## Coming up from the bottom of U on the other side:
                x = self.skip128usUP(x)          
                for i,skip128 in enumerate(self.skip128UP_arr[:self.depth//4]):
                    x = skip128(x)                
                x[:,:num_channels_to_save3,:,:] =  save_for_upside_3
                x = self.bn1UP(x)
                for i,skip128 in enumerate(self.skip128UP_arr[:self.depth//4]):
                    x = skip128(x)                
                x = self.skip128to64UP(x)
                for i,skip64 in enumerate(self.skip64UP_arr[self.depth//4:]):
                    x = skip64(x)                
                x[:,:num_channels_to_save2,:,:] =  save_for_upside_2
                x = self.bn2UP(x)
                x = self.skip64usUP(x)
                for i,skip64 in enumerate(self.skip64UP_arr[:self.depth//4]):
                    x = skip64(x)                
                x[:,:num_channels_to_save1,:,:] =  save_for_upside_1
                x = self.conv_out(x)
                return x
        

        class SegmentationLoss(nn.Module):
            """
            I wrote this class before I switched to MSE loss.  I am leaving it here
            in case I need to get back to it in the future.  

            Class Path:   DLStudio  ->  SemanticSegmentation  ->  SegmentationLoss
            """
            def __init__(self, batch_size):
                super(DLStudio.SemanticSegmentation.SegmentationLoss, self).__init__()
                self.batch_size = batch_size
            def forward(self, output, mask_tensor):
                composite_loss = torch.zeros(1,self.batch_size)
                mask_based_loss = torch.zeros(1,5)
                for idx in range(self.batch_size):
                    outputh = output[idx,0,:,:]
                    for mask_layer_idx in range(mask_tensor.shape[0]):
                        mask = mask_tensor[idx,mask_layer_idx,:,:]
                        element_wise = (outputh - mask)**2                   
                        mask_based_loss[0,mask_layer_idx] = torch.mean(element_wise)
                    composite_loss[0,idx] = torch.sum(mask_based_loss)
                return torch.sum(composite_loss) / self.batch_size


        def run_code_for_training_for_semantic_segmentation(self, net):        
            filename_for_out1 = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE1 = open(filename_for_out1, 'w')
            net = copy.deepcopy(net)
            net = net.to(self.dl_studio.device)
            criterion1 = nn.MSELoss()
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            start_time = time.perf_counter()
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss_segmentation = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    im_tensor,mask_tensor,bbox_tensor =data['image'],data['mask_tensor'],data['bbox_tensor']
                    im_tensor   = im_tensor.to(self.dl_studio.device)
                    mask_tensor = mask_tensor.type(torch.FloatTensor)
                    mask_tensor = mask_tensor.to(self.dl_studio.device)                 
                    bbox_tensor = bbox_tensor.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    output = net(im_tensor) 
                    segmentation_loss = criterion1(output, mask_tensor)  
                    segmentation_loss.backward()
                    optimizer.step()
                    running_loss_segmentation += segmentation_loss.item()    
                    if i%500==499:    
                        current_time = time.perf_counter()
                        elapsed_time = current_time - start_time
                        avg_loss_segmentation = running_loss_segmentation / float(500)
                        print("[epoch=%d/%d, iter=%4d  elapsed_time=%3d secs]   MSE loss: %.3f" % (epoch+1, self.dl_studio.epochs, i+1, elapsed_time, avg_loss_segmentation))
                        FILE1.write("%.3f\n" % avg_loss_segmentation)
                        FILE1.flush()
                        running_loss_segmentation = 0.0
            print("\nFinished Training\n")
            self.save_model(net)


        def save_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)


        def run_code_for_testing_semantic_segmentation(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            batch_size = self.dl_studio.batch_size
            image_size = self.dl_studio.image_size
            max_num_objects = self.max_num_objects
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    im_tensor,mask_tensor,bbox_tensor =data['image'],data['mask_tensor'],data['bbox_tensor']
                    if i % 50 == 0:
                        print("\n\n\n\nShowing output for test batch %d: " % (i+1))
                        outputs = net(im_tensor)                        
                        ## In the statement below: 1st arg for batch items, 2nd for channels, 3rd and 4th for image size
                        output_bw_tensor = torch.zeros(batch_size,1,image_size[0],image_size[1], dtype=float)
                        for image_idx in range(batch_size):
                            for layer_idx in range(max_num_objects): 
                                for m in range(image_size[0]):
                                    for n in range(image_size[1]):
                                        output_bw_tensor[image_idx,0,m,n]  =  torch.max( outputs[image_idx,:,m,n] )
                        display_tensor = torch.zeros(7 * batch_size,3,image_size[0],image_size[1], dtype=float)
                        for idx in range(batch_size):
                            for bbox_idx in range(max_num_objects):   
                                bb_tensor = bbox_tensor[idx,bbox_idx]
                                for k in range(max_num_objects):
                                    i1 = int(bb_tensor[k][1])
                                    i2 = int(bb_tensor[k][3])
                                    j1 = int(bb_tensor[k][0])
                                    j2 = int(bb_tensor[k][2])
                                    output_bw_tensor[idx,0,i1:i2,j1] = 255
                                    output_bw_tensor[idx,0,i1:i2,j2] = 255
                                    output_bw_tensor[idx,0,i1,j1:j2] = 255
                                    output_bw_tensor[idx,0,i2,j1:j2] = 255
                                    im_tensor[idx,0,i1:i2,j1] = 255
                                    im_tensor[idx,0,i1:i2,j2] = 255
                                    im_tensor[idx,0,i1,j1:j2] = 255
                                    im_tensor[idx,0,i2,j1:j2] = 255
                        display_tensor[:batch_size,:,:,:] = output_bw_tensor
                        display_tensor[batch_size:2*batch_size,:,:,:] = im_tensor

                        for batch_im_idx in range(batch_size):
                            for mask_layer_idx in range(max_num_objects):
                                for i in range(image_size[0]):
                                    for j in range(image_size[1]):
                                        if mask_layer_idx == 0:
                                            if 25 < outputs[batch_im_idx,mask_layer_idx,i,j] < 85:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 255
                                            else:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 50
                                        elif mask_layer_idx == 1:
                                            if 65 < outputs[batch_im_idx,mask_layer_idx,i,j] < 135:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 255
                                            else:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 50
                                        elif mask_layer_idx == 2:
                                            if 115 < outputs[batch_im_idx,mask_layer_idx,i,j] < 185:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 255
                                            else:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 50
                                        elif mask_layer_idx == 3:
                                            if 165 < outputs[batch_im_idx,mask_layer_idx,i,j] < 230:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 255
                                            else:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 50
                                        elif mask_layer_idx == 4:
                                            if outputs[batch_im_idx,mask_layer_idx,i,j] > 210:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 255
                                            else:
                                                outputs[batch_im_idx,mask_layer_idx,i,j] = 50

                                display_tensor[2*batch_size+batch_size*mask_layer_idx+batch_im_idx,:,:,:]= outputs[batch_im_idx,mask_layer_idx,:,:]
                        self.dl_studio.display_tensor_as_image(
                           torchvision.utils.make_grid(display_tensor, nrow=batch_size, normalize=True, padding=2, pad_value=10))




    ###%%%
    #####################################################################################################################
    ####################################  Start Definition of Inner Class Autoencoder  ##################################

    class Autoencoder(nn.Module):             
        """
         The man reason for the existence of this inner class in DLStudio is for it to serve as the base class for VAE 
         (Variational Auto-Encoder).  That way, the VAE class can focus exclusively on the random-sampling logic 
         specific to variational encoding while the base class Autoencoder does the convolutional and 
         transpose-convolutional heavy lifting associated with the usual encoding-decoding of image data.

        Class Path:   DLStudio  ->  Autoencoder
        """
        def __init__(self, dl_studio, encoder_in_im_size, encoder_out_im_size, decoder_out_im_size, encoder_out_ch, num_repeats, path_saved_model):
            super(DLStudio.Autoencoder, self).__init__()
            self.dl_studio = dl_studio
            ## The parameter num_repeats is how many times you want to repeat in the Encoder the SkipBlock that has the same number of
            ## channels at the input and the output (See the code for EncoderForAutoenc):
            self.encoder  =  DLStudio.Autoencoder.EncoderForAutoenc( dl_studio, encoder_in_im_size, encoder_out_im_size, encoder_out_ch, num_repeats)
            decoder_in_im_size = encoder_out_im_size
            self.decoder  =  DLStudio.Autoencoder.DecoderForAutoenc( dl_studio, decoder_in_im_size, decoder_out_im_size )
            self.path_saved_model = path_saved_model

        def forward(self, x):   
            x =  self.encoder(x)                                                                                             
            x =  self.decoder(x)                                                                                             
            return x             


        class EncoderForAutoenc(nn.Module):
            """
            The two main components of an Autoencoder are the encoder and the decoder. This is the encoder part of the 
             Autoencoder.

            The parameter num_repeats is how many times you want to repeat in the Encoder the SkipBlock that has the same 
            number of channels at the input and the output.

            Class Path:   DLStudio  ->  Autoencoder  ->  EncoderForAutoenc
            """ 
            def __init__(self, dl_studio, encoder_in_im_size, encoder_out_im_size, encoder_out_ch, num_repeats, skip_connections=True):
                super(DLStudio.Autoencoder.EncoderForAutoenc, self).__init__()
                downsampling_ratio =  encoder_in_im_size[0] // encoder_out_im_size[0]
                num_downsamples =  downsampling_ratio // 2
                assert( num_downsamples == 1 or num_downsamples == 2 or num_downsamples == 4 )
                self.depth = num_downsamples
                self.encoder_out_im_size = encoder_out_im_size
                self.encoder_out_ch = encoder_out_ch
                self.conv_in = nn.Conv2d(3, 64, 3, padding=1)
                self.bn1DN  = nn.BatchNorm2d(64)
                self.bn2DN  = nn.BatchNorm2d(128)
                self.bn3DN  = nn.BatchNorm2d(256)
                self.skip_arr = nn.ModuleList()
                if self.depth == 1:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(64, 64, downsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(64, 128, downsample=False, skip_connections=skip_connections))
                    for _ in range(num_repeats):
                        self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 128, downsample=False, skip_connections=skip_connections))
                elif self.depth == 2:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(64, 64, downsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(64, 128, downsample=False, skip_connections=skip_connections))
                    for _ in range(num_repeats):
                        self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 128, downsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 128, downsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 256, downsample=False, skip_connections=skip_connections))
                    for _ in range(num_repeats):
                        self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(256, 256, downsample=False, skip_connections=skip_connections))
                elif self.depth == 4:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(64, 64, downsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(64, 128, downsample=False, skip_connections=skip_connections))
                    for _ in range(num_repeats):
                        self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 128, downsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 128, downsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(128, 256, downsample=False, skip_connections=skip_connections))
                    for _ in range(num_repeats):
                        self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(256, 256, downsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(256, 256, downsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(256, 512, downsample=False, skip_connections=skip_connections))
                    for _ in range(num_repeats):
                        self.skip_arr.append(DLStudio.Autoencoder.SkipBlockEncoder(512, 512, downsample=False, skip_connections=skip_connections))
                self.skip128DN = DLStudio.Autoencoder.SkipBlockEncoder(128,128, skip_connections=skip_connections)

            def forward(self, x):
                x = nn.functional.relu(self.conv_in(x))          
                for layer in self.skip_arr:
                    x = layer(x)
                if (x.shape[2:] != self.encoder_out_im_size) or (x.shape[1] != self.encoder_out_ch):
                    print("\n\nShape of x at output of Encoder: ", x.shape) 
                    sys.exit("\n\nThe Encoder part of the Autoencoder is misconfigured. Encoder output not according to specs\n\n")
                return x


        class DecoderForAutoenc(nn.Module):
            """
            The two main components of an Autoencoder are the encoder and the decoder.
            This is the decoder part of the Autoencoder.

            This Decoder uses bilinear interpolation for final upsampling.           XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

            The next Decoder that follows is based on using nn.ConvTranspose2d for upsampling.

            Class Path:   DLStudio  ->  Autoencoder  ->  DecoderForAutoenc
            """ 
            def __init__(self, dl_studio, decoder_in_im_size, decoder_out_im_size, skip_connections=True):
                super(DLStudio.Autoencoder.DecoderForAutoenc, self).__init__()
                upsampling_ratio =  decoder_out_im_size[0] // decoder_in_im_size[0]
                num_upsamples =  upsampling_ratio // 2
                assert( num_upsamples == 1 or num_upsamples == 2 or num_upsamples == 4)
                self.depth = num_upsamples
                self.decoder_out_im_size = decoder_out_im_size
                self.conv_in = nn.Conv2d(3, 64, 3, padding=1)
                self.bn1DN  = nn.BatchNorm2d(64)
                self.bn2DN  = nn.BatchNorm2d(128)
                self.bn3DN  = nn.BatchNorm2d(256)
                self.skip_arr = nn.ModuleList()
                if self.depth == 1:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 64, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(64, 64, upsample=True, skip_connections=skip_connections))
                elif self.depth == 2:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(256, 128, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 128, upsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 64, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(64, 64, upsample=True, skip_connections=skip_connections))
                elif self.depth == 4:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(512, 256, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(256, 256, upsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(256, 128, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 128, upsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 64, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(64, 64, upsample=True, skip_connections=skip_connections))
                self.bn1UP  = nn.BatchNorm2d(256)
                self.bn2UP  = nn.BatchNorm2d(128)
                self.bn3UP  = nn.BatchNorm2d(64)
#                self.conv_out3 = nn.ConvTranspose2d(64,3, 3, stride=1,dilation=1,output_padding=0,padding=1)
                self.conv_out3 = nn.Conv2d(64,3,3,padding=1)

            def forward(self, x):
                for layer in self.skip_arr:
                    x = layer(x)
                x = self.conv_out3(x)
                if x.shape[2:] != self.decoder_out_im_size:
                    print("\n\nShape of x at output of Decoder: ", x.shape) 
                    sys.exit("\n\nThe Decoder part of the Autoencoder is misconfigured. Output image not according to specs\n\n")
                return x


        class DecoderForAutoenc_CT(nn.Module):
            """
            The "_CT" in the name of this class signifies that this Decoder uses ConvTranspose layers for upsampling.

            Note that using nn.ConvTranspose for upsampling may introducing gridding artifacts in the output images.

            Class Path:   DLStudio  ->  Autoencoder  ->  DecoderForAutoenc_CT
            """ 
            def __init__(self, dl_studio, decoder_in_im_size, decoder_out_im_size, skip_connections=True):
                super(DLStudio.Autoencoder.DecoderForAutoenc_CT, self).__init__()
                upsampling_ratio =  decoder_out_im_size[0] // decoder_in_im_size[0]
                num_upsamples =  upsampling_ratio // 2
                assert( num_upsamples == 1 or num_upsamples == 2 or num_upsamples == 4)
                self.depth = num_upsamples
                self.decoder_out_im_size = decoder_out_im_size
                self.conv_in = nn.Conv2d(3, 64, 3, padding=1)
                self.bn1DN  = nn.BatchNorm2d(64)
                self.bn2DN  = nn.BatchNorm2d(128)
                self.bn3DN  = nn.BatchNorm2d(256)
                self.skip_arr = nn.ModuleList()
                if self.depth == 1:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 64, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(64, 64, upsample=True, skip_connections=skip_connections))
                elif self.depth == 2:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(256, 128, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 128, upsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 64, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(64, 64, upsample=True, skip_connections=skip_connections))
                elif self.depth == 4:
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(512, 256, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(256, 256, upsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(256, 128, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 128, upsample=True, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(128, 64, upsample=False, skip_connections=skip_connections))
                    self.skip_arr.append(DLStudio.Autoencoder.SkipBlockDecoder(64, 64, upsample=True, skip_connections=skip_connections))
                self.bn1UP  = nn.BatchNorm2d(256)
                self.bn2UP  = nn.BatchNorm2d(128)
                self.bn3UP  = nn.BatchNorm2d(64)
                self.conv_out3 = nn.ConvTranspose2d(64,3, 3, stride=1,dilation=1,output_padding=0,padding=1)

            def forward(self, x):
                for layer in self.skip_arr:
                    x = layer(x)
                x = self.conv_out3(x)
                if x.shape[2:] != self.decoder_out_im_size:
                    print("\n\nShape of x at output of Decoder: ", x.shape) 
                    sys.exit("\n\nThe Decoder part of the Autoencoder is misconfigured. Output image not according to specs\n\n")
                return x


        def save_autoencoder_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_model)


        def run_code_for_training_autoencoder( self, display_train_loss=False ):
      
            autoencoder = self.to(self.dl_studio.device)
            criterion = nn.MSELoss()
            optimizer = optim.Adam(autoencoder.parameters(), lr=self.dl_studio.learning_rate)
            accum_times = []
            start_time = time.perf_counter()
            training_loss_tally = []
            print("")
            batch_size = self.dl_studio.batch_size
            print("\n\n batch_size: ", batch_size)
            print("\n\n number of batches in the dataset: ", len(self.train_dataloader))
    
            for epoch in range(self.dl_studio.epochs):                                                              
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):                                    
                    input_images, _ = data       
                    input_images = input_images.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    autoencoder_output = autoencoder( input_images )
                    loss  =  criterion( autoencoder_output, input_images )
                    loss.backward()                                                                                        
                    optimizer.step()
                    running_loss += loss
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss.item())
                        running_loss = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%2d/%2d  i:%4d  elapsed_time: %4d secs]     loss: %.4f" % (epoch+1, self.dl_studio.epochs, i+1,time_elapsed,avg_loss)) 
                        accum_times.append(current_time-start_time)
            print("\nFinished Training\n")
            self.save_autoencoder_model( autoencoder )
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()
    


        def run_code_for_evaluating_autoencoder(self, visualization_dir = "autoencoder_visualization_dir" ):
    
            if os.path.exists(visualization_dir):  
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   
            autoencoder = self
            autoencoder.load_state_dict(torch.load(self.path_saved_model))
            autoencoder.to(self.dl_studio.device)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):                                    
                    print("\n\n\n=========Showing results for test batch %d===============" % i)
                    test_images, _ = data     

                    test_images = test_images.to(self.dl_studio.device)
                    autoencoder_output = autoencoder( test_images )
                    autoencoder_output  =  ( autoencoder_output - autoencoder_output.min() ) / ( autoencoder_output.max() -  autoencoder_output.min() )
                    together = torch.zeros( test_images.shape[0], test_images.shape[1], test_images.shape[2], 2 * test_images.shape[3], dtype=torch.float )
                    together[:,:,:,0:test_images.shape[3]]  =  test_images
                    together[:,:,:,test_images.shape[3]:]  =   autoencoder_output 

                    plt.figure(figsize=(40,20))
                    plt.imshow(np.transpose(torchvision.utils.make_grid(together.cpu(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                    plt.title("Autoencoder Output Images for iteration %d" % i)
                    plt.savefig(visualization_dir + "/autoenc_output_%s" % str(i) + ".png")
                    plt.show()

    

        class SkipBlockEncoder(nn.Module):
            """
            This is a building-block class for the skip connections in EncoderForAutoenc

            Class Path:   DLStudio  ->  Autoencoder  ->  SkipBlockEncoder
            """
            def __init__(self, in_ch, out_ch, downsample=False, skip_connections=True):
                super(DLStudio.Autoencoder.SkipBlockEncoder, self).__init__()
                self.downsample = downsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convo1 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
                self.convo2 = nn.Conv2d(in_ch, out_ch, 3, stride=1, padding=1)
#                self.bn1 = nn.BatchNorm2d(out_ch)
                self.gn1 = nn.GroupNorm(num_groups=32, num_channels=out_ch, eps=1e-6, affine=True)   
#                self.bn2 = nn.BatchNorm2d(out_ch)
                self.gn2 = nn.GroupNorm(num_groups=32, num_channels=out_ch, eps=1e-6, affine=True)   
                if downsample:
                    self.downsampler = nn.Conv2d(in_ch, out_ch, 1, stride=2)

            def forward(self, x):
                identity = x                                     
                out = self.convo1(x)                              
#                out = self.bn1(out)                              
                out = self.gn1(out)                              
                out = nn.functional.relu(out)
                if self.in_ch == self.out_ch:
                    out = self.convo2(out)                              
#                    out = self.bn2(out)                              
                    out = self.gn2(out)                              
                    out = nn.functional.relu(out)
                if self.downsample:
                    out = self.downsampler(out)
                    identity = self.downsampler(identity)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity
                    else:
                        out = out + torch.cat((identity, identity), dim=1) 
                return out

        class SkipBlockDecoder(nn.Module):
            """
            This is a building-block class for the skip connections in DecoderForAutoenc

            This SkipBlock is based on using interpolation for upsampling.

            Class Path:   DLStudio  ->  Autoencoder  ->  SkipBlockDecoder
            """
            def __init__(self, in_ch, out_ch, upsample=False, skip_connections=True):
                super(DLStudio.Autoencoder.SkipBlockDecoder, self).__init__()
                self.upsample = upsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.conv1 = nn.Conv2d(in_ch, out_ch, 3,padding=1)
                self.conv2 = nn.Conv2d(in_ch, out_ch, 3,padding=1)
                self.conv3 = nn.Conv2d(out_ch, out_ch, 3,padding=1)
#                self.bn1 = nn.BatchNorm2d(out_ch)
                self.gn1 = nn.GroupNorm(num_groups=32, num_channels=out_ch, eps=1e-6, affine=True)   
#                self.bn2 = nn.BatchNorm2d(out_ch)
                self.gn2 = nn.GroupNorm(num_groups=32, num_channels=out_ch, eps=1e-6, affine=True)   
                self.gn3 = nn.GroupNorm(num_groups=32, num_channels=out_ch, eps=1e-6, affine=True)   

            def forward(self, x):
                identity = x                                     
                out = self.conv1(x)
#                out = self.bn1(out) 
                out = self.gn1(out) 
                out = nn.functional.relu(out)
                if self.in_ch == self.out_ch:
                    out = self.conv2(out)                              
#                    out = self.bn2(out)                              
                    out = self.gn2(out)                              
                    out = nn.functional.relu(out)
                if self.upsample:
                    ## This is the ONLY part where upsampling takes place in this skip block
                    out = F.interpolate(out, scale_factor=2.0)
                    identity = F.interpolate(identity, scale_factor=2.0)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity                              
                    else:
                        out = out + identity[:,self.out_ch:,:,:]
                out = self.conv3(out)
                out = self.gn3(out)                              
                out = nn.functional.relu(out)
                return out


        class SkipBlockDecoder_CT(nn.Module):
            """
            This is a building-block class for the skip connections in DecoderForAutoenc

            This class uses convTranspose layers for upsampling

            Class Path:   DLStudio  ->  Autoencoder  ->  SkipBlockDecoder
            """
            def __init__(self, in_ch, out_ch, upsample=False, skip_connections=True):
                super(DLStudio.Autoencoder.SkipBlockDecoder_CT, self).__init__()
                self.upsample = upsample
                self.skip_connections = skip_connections
                self.in_ch = in_ch
                self.out_ch = out_ch
                self.convoT1 = nn.ConvTranspose2d(in_ch, out_ch, 3, padding=1)
                self.convoT2 = nn.ConvTranspose2d(in_ch, out_ch, 3, padding=1)
                self.bn1 = nn.BatchNorm2d(out_ch)
                self.bn2 = nn.BatchNorm2d(out_ch)
                if upsample:
                    self.upsampler = nn.ConvTranspose2d(in_ch, out_ch, 1, stride=2, dilation=2, output_padding=1, padding=0)
            def forward(self, x):
                identity = x                                     
                out = self.convoT1(x)                              
                out = self.bn1(out)                              
                out  =  nn.ReLU(inplace=False)(out)            
                if self.in_ch == self.out_ch:
                    out = self.convoT2(out)                              
                    out = self.bn2(out)                              
                    out = nn.functional.relu(out)
                if self.upsample:
                    out = self.upsampler(out)
                    identity = self.upsampler(identity)
                if self.skip_connections:
                    if self.in_ch == self.out_ch:
                        out = out + identity                              
                    else:
                        out = out + identity[:,self.out_ch:,:,:]
                return out


        def set_dataloader(self):
            """
            Note the call to random_split() in the second statement for dividing the overall dataset of images into 
            two DISJOINT parts, one for training and the other for testing.  Since my evaluation of the VAE at this
            time is purely on the basis of the visual quality of the output of the Decoder, I have set aside only
            200 randomly chosen images for testing.  Ordinarily, through, you would want to split the dataset in 
            the 70:30 or 80:20 ratio for training and testing.
            """
            dataset = torchvision.datasets.ImageFolder(root=self.dl_studio.dataroot,       
                           transform = tvt.Compose([                 
                                                tvt.Resize(self.dl_studio.image_size),             
                                                tvt.CenterCrop(self.dl_studio.image_size),         
                                                tvt.ToTensor(),                     
                                                tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),         
                           ]))

            dataset_train, dataset_test  =  torch.utils.data.random_split( dataset, lengths = [len(dataset) - 200, 200])

            self.train_dataloader = torch.utils.data.DataLoader(dataset_train, batch_size=self.dl_studio.batch_size, shuffle=True, num_workers=4)
            self.test_dataloader = torch.utils.data.DataLoader(dataset_test, batch_size=self.dl_studio.batch_size, shuffle=True, num_workers=4)



    ###%%%
    #####################################################################################################################
    #######################################  Start Definition of Inner Class VAE  #######################################

    class VAE (Autoencoder):             
        """
        VAE stands for "Variational Auto Encoder".  These days, you are more likely to see it
        written as "variational autoencoder".  I consider VAE as one of the foundational neural
        architectures in Deep Learning.  VAE is based on the new celebrated 2014 paper 
        "Auto-Encoding Variational Bayes" by Kingma and Welling.  The idea is for the Encoder 
        part of an Encoder-Decoder pair to learn the probability distribution for the Latent 
        Space Representation of a training dataset.  Described loosely, the latent vector z for 
        an input image x would be the "essence" of what x is depicting.  Presumably, after the
        latent distribution has been learned, the Decoder should be able to transform any "noise" 
        vector sampled from the latent distribution and convert it into the sort of output you 
        would see during the training process.

        In case you are wondering about the dimensionality of the Latent Space, consider the case
        that the input images are eventually converted into 8x8 pixel arrays, with each pixel
        represented by a 128-dimensional embedding.  In a vectorized representation, this implies
        an 8192-dimensional space for the Latent Distribution.  The mean (mu) and the log-variance
        values (logvar) values learned by the Encoder would represent vectors in an 8,192 
        dimensional space.  The Decoder's job would be sample this distribution and attempt a
        reconstruction of what the user wants to see at the output of the Decoder.

        As you can see, the VAE class is derived from the parent class Autoencoder.  Bulk of the
        computing in VAE is done through the functionality packed into the Autoencoder class.
        Therefore, in order to fully understand the VAE implementation here, your starting point
        should be the code for the Autoencoder class.  

        Class Path:   DLStudio  ->  VAE
        """  

        def __init__(self, dl_studio, encoder_in_im_size, encoder_out_im_size, decoder_out_im_size, encoder_out_ch, num_repeats, path_saved_encoder, path_saved_decoder ):
            super(DLStudio.VAE, self).__init__( dl_studio, encoder_in_im_size, encoder_out_im_size, decoder_out_im_size, encoder_out_ch, num_repeats, path_saved_model=None )
            self.parent_encoder =  DLStudio.Autoencoder.EncoderForAutoenc(dl_studio, encoder_in_im_size, encoder_out_im_size, encoder_out_ch, num_repeats, skip_connections=True )
            self.parent_decoder =  DLStudio.Autoencoder.DecoderForAutoenc(dl_studio, encoder_out_im_size, decoder_out_im_size)
            self.vae_encoder =  DLStudio.VAE.VaeEncoder(self.parent_encoder, encoder_out_im_size, encoder_out_ch)      
            self.vae_decoder =  DLStudio.VAE.VaeDecoder(self.parent_decoder, encoder_out_im_size, encoder_out_ch)
            self.encoder_out_im_size = self.encoder.encoder_out_im_size
            self.encoder_out_ch  =  self.encoder.encoder_out_ch
            self.path_saved_encoder = path_saved_encoder
            self.path_saved_decoder = path_saved_decoder


        class VaeEncoder(nn.Module):
            """
            The most important thing to note here is that this Encoder outputs ONLY the mean and the log-variance
            of the Gaussian distribution that models the latent vectors. VAEs are based on the assumption that 
            Latent Distributions are far simpler than the probability distributions that would model the image
            dataset used for training.

            Class Path:   DLStudio  ->  VAE  ->  VaeEncoder
            """
            def __init__(self, parent_encoder, encoder_out_im_size, encoder_out_ch):
                super(DLStudio.VAE.VaeEncoder, self).__init__()
                self.parent_encoder = parent_encoder
                self.num_nodes = encoder_out_im_size[0] * encoder_out_im_size[1]  * encoder_out_ch
                self.latent_dim = encoder_out_ch
                self.mu_layer =  nn.Linear(self.num_nodes, self.latent_dim)
                self.log_var_layer =  nn.Linear(self.num_nodes, self.latent_dim)

            def forward(self, x):
               encoded = self.parent_encoder(x)
               mu  = self.mu_layer(encoded.view(-1, self.num_nodes))        
               log_var = self.log_var_layer(encoded.view(-1, self.num_nodes))
               return mu, log_var


        class VaeDecoder(nn.Module):
            """
            The VAE Decoder's job is to take the mu and logvar values produced by the Encoder and
            generate an output image that contains the information that the user wants to see there.
            For obvious reasons, as to what exactly is seen at the output of the Decoder would 
            depend on the loss function used and the shape of the output tensor.  If all you wanted
            to see was a reduced dimensionality image at the output, you would need to change the
            final layers of the Decoder so that the final output corresponds to the shape that goes
            with that representation.

            Class Path:   DLStudio  ->  VAE  ->  VaeDecoder
            """
            def __init__(self, parent_decoder, encoder_out_im_size, encoder_out_ch):
                super(DLStudio.VAE.VaeDecoder, self).__init__()
                self.parent_decoder = parent_decoder
                self.encoder_out_im_size = encoder_out_im_size
                self.num_nodes = encoder_out_im_size[0] * encoder_out_im_size[1]  * encoder_out_ch
                self.latent_dim = encoder_out_ch
                self.reparametrized_to_decoder_input = nn.Linear(self.latent_dim, self.num_nodes)

            def reparameterize(self, mu, logvar):
               std  =  torch.exp(0.5 * logvar)

               ##  In the next statement, 'torch.randn' is sampling from an isotropic zero-mean 
               ##  unit-covariance Gaussian.  The call 'torch.randn_like' ensures that the returned 
               ##  tensor will have the same shape as the 'std' tensor.  
               ##
               ##  In order to understand the shape of 'std', consider the case when the size of the
               ##  pixel array at the Encoder output is 8x8, the embedding size 128, and the 
               ##  batch_size 48.  In this case, you have 64 pixels at the output of the Encoder 
               ##  (before you go into the Linear layers for mu and logvar estimation). So the 
               ##  shape of both 'logvar' and 'std' is going to be [48, 8192] where 8192 is the product 
               ##  of the 64 pixels and the 128 channels at each pixel.  Note that the shapes for all 
               ##  three of 'mu', 'logvar', and 'std' are identical and, for our example, that shape is
               ##  [48, 8192].
               eps =  torch.randn_like( std )                    ## standard normal N(0;1)
               return mu + eps * std

            def forward(self, mu, logvar):
               z = self.reparameterize( mu, logvar )
               z = self.reparametrized_to_decoder_input(z)
               decoded = self.parent_decoder( z.view(-1, self.latent_dim, self.encoder_out_im_size[0], self.encoder_out_im_size[1]) )
               return decoded, mu, logvar


        def save_encoder_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_encoder)


        def save_decoder_model(self, model):
            '''
            Save the trained model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_decoder)



        def run_code_for_training_VAE( self, vae_net, loss_weighting, display_train_loss=False ):
            """
            The code for set_dataloaders() for the VAE class shows how the overall dataset of images is divided into
            training and testing subsets.  

            The important thing to keep in mind about this function is the relative weighting of the reconstruction
            loss vis-a-vis the KL-divergence.  For an "optimized" VAE implementation, finding the best value to use
            for this relative weighting of the two loss components would be a part of hyperparameter tuning of the
            network.
            """            
            def loss_criterion(input_images, decoder_output_images, log_var, weighting):
                recon_loss = nn.MSELoss(reduction='sum')( input_images, decoder_output_images )   ## reconstruction loss
                KLD = -0.5 * torch.sum( 1 + log_var - mu.pow(2)  -  log_var.exp() )               ## KL Divergence
                KLD =  KLD * weighting
                return  recon_loss + KLD,  recon_loss, KLD

            vae_encoder = vae_net.vae_encoder.to(self.dl_studio.device)
            vae_decoder = vae_net.vae_decoder.to(self.dl_studio.device)
            accum_times = []
            start_time = time.perf_counter()
            print("")
            batch_size = self.dl_studio.batch_size
            print("\n\n batch_size: ", batch_size)
            num_batches_in_data_source = len(self.train_dataloader)
            total_num_updates = self.dl_studio.epochs * num_batches_in_data_source
            print("\n\n number of batches in the dataset: ", num_batches_in_data_source)
            optimizer1 = optim.Adam(vae_encoder.parameters(), lr=self.dl_studio.learning_rate)     
            optimizer2 = optim.Adam(vae_decoder.parameters(), lr=self.dl_studio.learning_rate)     
            mu = logvar = 0.0

            total_training_loss_tally = []
            recons_loss_tally = []
            KL_divergence_tally = []

            for epoch in range(self.dl_studio.epochs):                                                              
                print("")
                ##  The following are needed for calculating the avg values between displays:
                running_loss = running_recon_loss = running_kld_loss = 0.0
                for i, data in enumerate(self.train_dataloader):                                    
                    input_images, _ = data                              
                    input_images = input_images.to(self.dl_studio.device)
                    optimizer1.zero_grad()
                    optimizer2.zero_grad()
                    mu, logvar =  vae_encoder( input_images )
                    ##  As required by VAE, the Decoder is only being supplied with the mean 'mu' and the log-variance 'logvar':
                    decoder_out, _, _ =  vae_decoder( mu, logvar )    
                    loss, recon_loss, kld_loss  =  loss_criterion( input_images,  decoder_out, logvar, loss_weighting )
                    loss.backward()                                                                                        
                    optimizer1.step()
                    optimizer2.step()
                    running_loss += loss
                    running_recon_loss += recon_loss
                    running_kld_loss += kld_loss
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        avg_recon_loss = running_recon_loss / float(200)
                        avg_kld_loss = running_kld_loss / float(200)
                        total_training_loss_tally.append(avg_loss.item())
                        recons_loss_tally.append(avg_recon_loss.item())
                        KL_divergence_tally.append(avg_kld_loss.item())
                        running_loss = running_recon_loss = running_kld_loss = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%2d/%2d  i:%4d  elapsed_time: %4d secs]     loss: %10.4f      recon_loss: %10.4f      kld_loss:  %10.4f " % 
                                               (epoch+1, self.dl_studio.epochs, i+1,time_elapsed,avg_loss,avg_recon_loss,avg_kld_loss)) 
                        accum_times.append(current_time-start_time)

            print("\nFinished Training\n")
            self.save_encoder_model( vae_encoder )
            self.save_decoder_model( vae_decoder )

            params_saved = { 'mean': mu, 'log_variance': logvar}
            pickle.dump(params_saved, open('params_saved.p', 'wb'))

            if display_train_loss:

                fig, (ax1,ax2,ax3) = plt.subplots(nrows=1, ncols=3, figsize=(20,5))

                ax1.plot(total_training_loss_tally)
                ax2.plot(recons_loss_tally)                                  
                ax3.plot(KL_divergence_tally)                                  

                ax1.set_xticks(np.arange(total_num_updates // 200))    ## since each val for plotting is generated every 200 iterations
                ax2.set_xticks(np.arange(total_num_updates // 200))
                ax3.set_xticks(np.arange(total_num_updates // 200))

                ax1.set_xlabel("iterations") 
                ax2.set_xlabel("iterations") 
                ax3.set_xlabel("iterations") 

                ax1.set_ylabel("total training loss") 
                ax2.set_ylabel("reconstruction loss") 
                ax3.set_ylabel("KL divergence") 

                plt.savefig("all_training_losses.png")
                plt.show()
   


        def run_code_for_evaluating_VAE(self, vae_net, visualization_dir = "vae_visualization_dir" ):
            """
            The main point here is to use the co-called "unseen images" for evaluating the performance
            of the VAE Encoder-Decoder network.  If you look at the set_dataloader() function for the
            VAE class, you will see me setting aside a certain number of the available images for testing.
            These randomly chosen images play NO role in training.
            """
    
            if os.path.exists(visualization_dir):  
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   
     
            vae_encoder = vae_net.vae_encoder.eval()
            vae_decoder = vae_net.vae_decoder.eval()
            vae_encoder.load_state_dict(torch.load(self.path_saved_encoder))
            vae_decoder.load_state_dict(torch.load(self.path_saved_decoder))
            vae_encoder.to(self.dl_studio.device) 
            vae_decoder.to(self.dl_studio.device)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):                                    
                    print("\n\n\n=========Showing results for test batch %d===============" % i)
                    test_images, _ = data     
                    test_images = test_images.to(self.dl_studio.device)
                    mu, logvar =  vae_encoder( test_images )
                    ##  In the next statement, using mu and logvar, the Decoder first uses the "reparameterization trick" 
                    ##  to sample the latent distribution and to then feed it into the rest of the Decoder for image generation:
                    decoder_out, _, _ =  vae_decoder( mu, logvar )   
                    decoder_out  =  ( decoder_out - decoder_out.min() ) / ( decoder_out.max() -  decoder_out.min() )
                    together = torch.zeros( test_images.shape[0], test_images.shape[1], test_images.shape[2], 2 * test_images.shape[3], dtype=torch.float )
                    together[:,:,:,0:test_images.shape[3]]  =  test_images
                    together[:,:,:,test_images.shape[3]:]  =   decoder_out 
                    plt.figure(figsize=(40,20))
                    plt.imshow(np.transpose(torchvision.utils.make_grid(together.cpu(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                    plt.title("VAE Output Images for iteration %d" % i)
                    plt.savefig(visualization_dir + "/vae_decoder_out_%s" % str(i) + ".png")
                    plt.show()



        def run_code_for_generating_images_from_noise_VAE(self, vae_net, visualization_dir = "vae_gen_visualization_dir" ):
            """
            This function is for testing the functioning of just the Generator (which is the Decoder) in
            the VAE network.  That is, after we have trained the VAE network, we disconnect the Encoder 
            and ask the Decoder to sample the latent distribution for generating the images.

            Remember, the latent distribution is represented entirely by the final values learned for 
            the mean (mu) and the log of the variance (logvar) that represent how close the training process
            was able to come to the ideal of zero-mean and unit-covariance isotropic distribution.
            Since the job of this function is to sample the latent distribution actually learned, we must
            also supply with the (mu,logvar) values learned during training.
            """
            if os.path.exists(visualization_dir):  
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   
     
            vae_decoder = vae_net.vae_decoder.eval()
            vae_decoder.load_state_dict(torch.load(self.path_saved_decoder))
            params_saved = pickle.load( open('params_saved.p', 'rb') )
            mu, logvar = params_saved['mean'], params_saved['log_variance']

            ##  The size of the batch axis for the mu and logvar tensors will corresponds to the number 
            ##  of images in the last batch used for training.  If you want the purely generative process
            ##  in this script (which uses the VAE Decoder in a standalone mode) to produce a batchful of 
            ##  images, you need to expand the previously learned mu and logvar tensors as shown below:
            if mu.shape[0] < self.dl_studio.batch_size:
                new_mu = torch.zeros( (self.dl_studio.batch_size, mu.shape[1]) ).float()  
                new_mu[:mu.shape[0]]  =  mu
                new_mu[mu.shape[0]:] = mu[:(self.dl_studio.batch_size - mu.shape[0])]

                new_logvar = torch.zeros( (self.dl_studio.batch_size, logvar.shape[1]) ).float()  
                new_logvar[:logvar.shape[0]]  = logvar
                new_logvar[logvar.shape[0]:] = logvar[:(self.dl_studio.batch_size - logvar.shape[0])]
            mu = new_mu.to(self.dl_studio.device)
            logvar = new_logvar.to(self.dl_studio.device)
            vae_decoder.to(self.dl_studio.device)
            sample_standard_normal_distribution = True
            sample_learned_normal_distribution =  False
            with torch.no_grad():
                for i in range(5):
                    print("\n\n\n=========Showing results for test batch %d===============" % i)
                    if sample_standard_normal_distribution:
                        mu  =  torch.zeros_like(mu).float().to(self.dl_studio.device)
                        logvar = torch.ones_like(logvar).float().to(self.dl_studio.device)
                    elif sample_learned_normal_distribution:
                        std = torch.exp(0.5 * logvar)
                    ##  In the next statement, using mu and logvar, the Decoder first uses the "reparameterization trick" 
                    ##  to sample the latent distribution and to then feed it into the rest of the Decoder for image generation:
                    decoder_out, _, _ =  vae_decoder( mu, logvar )   
                    decoder_out  =  ( decoder_out - decoder_out.min() ) / ( decoder_out.max() -  decoder_out.min() )
                    fake_input = torch.zeros_like(decoder_out).float().to(self.dl_studio.device)
                    together = torch.zeros( fake_input.shape[0], fake_input.shape[1], fake_input.shape[2], 2 * fake_input.shape[3], dtype=torch.float )
                    together[:,:,:,0:fake_input.shape[3]]  =  fake_input
                    together[:,:,:,fake_input.shape[3]:]  =   decoder_out 
                    plt.figure(figsize=(40,20))
                    plt.imshow(np.transpose(torchvision.utils.make_grid(together.cpu(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                    plt.title("VAE Output Images for iteration %d" % i)
                    plt.savefig(visualization_dir + "/vae_decoder_out_%s" % str(i) + ".png")
                    plt.show()


        def set_dataloader(self):
            """
            Note the call to random_split() in the second statement for dividing the overall dataset of images into 
            two DISJOINT parts, one for training and the other for testing.  Since my evaluation of the VAE at this
            time is purely on the basis of the visual quality of the output of the Decoder, I have set aside only
            200 randomly chosen images for testing.  Ordinarily, through, you would want to split the dataset in 
            the 70:30 or 80:20 ratio for training and testing.
            """
            dataset = torchvision.datasets.ImageFolder(root=self.dl_studio.dataroot,       
                           transform = tvt.Compose([                 
                                                tvt.Resize(self.dl_studio.image_size),             
                                                tvt.CenterCrop(self.dl_studio.image_size),         
                                                tvt.ToTensor(),                     
                                                tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),         
                           ]))

            dataset_train, dataset_test  =  torch.utils.data.random_split( dataset, lengths = [len(dataset) - 200, 200])
            self.train_dataloader = torch.utils.data.DataLoader(dataset_train, batch_size=self.dl_studio.batch_size, shuffle=True, num_workers=4)
            self.test_dataloader = torch.utils.data.DataLoader(dataset_test, batch_size=self.dl_studio.batch_size, shuffle=True, num_workers=4)



    ###%%%
    #####################################################################################################################
    ######################################  Start Definition of Inner Class VQVAE  ######################################

    class VQVAE (Autoencoder):             
        """
        VQVAE is an important architecture in deep learning because it teaches us about what
        has come to be known as "Codebook Learning" for more efficient discrete representation
        of images with a finite vocabulary of embedding vectors.

        VQVAE stands for "Vector Quantized Variational Auto Encoder", which is also frequently
        represented by the acronym VQ-VAE.  The concept of VQ-VAE was formulated in the 2018
        publication "Neural Discrete Representation Learning" by van den Oord, Vinyals, and
        Kavukcuoglu.

        For the case of images, VQ-VAE means that we want to represent an input image using a
        user-specified number of embedding vectors.  You could think of the set of embedding
        vectors as constituting a fixed-size vocabulary for representing the input data.

        To make the definition of Codebook Learning more specific, say we are using an
        Encoder-Decoder to create such a fixed-vocabulary based representation for the images.
        Let's assume that the Encoder converts each input batch of images into a (B,C,H,W)
        shaped tensor where the height H and the width W are likely to be small numbers, say 8
        each, and C is likely to be, say, 128.  Let's also say that the batch size is 256.

        The total number of pixels in all the batch instances at the output of the Encoder will
        be B*H*W.  I'll represent this number of pixels with the notation BHW.  For the example
        numbers used above, BHW will be equal to 256*8*8 = 16384.

        Taking cognizance of the channel axis, we can say that each of the 16,384 pixels at the
        output of the Encoder is represented by a 128 element vector along the channel axis.

        As things stand, each C-dimensional pixel based vector at the output of the Encoder will
        be a continuous valued vector.

        The goal of VQ-VAE is define a Codebook of K vectors, each of dimension D, with the
        idea that each of the C-dimensional BHW vectors at the output of the Encode will be
        replaced by the closest of the K D-dimensional vectors in the Codebook.  For practical
        reasons, we require D=C.

        The Decoder's job then is to try its best to recreate the input using the Codebook
        approximations at the output of the Encoder.

        The goal of VQ-VAE is to demonstrate that it is possible to learn a Codebook with K
        elements that can subsequently be used to represent any input.

        You can think of the learned Codebook vectors as the quantized versions of what the
        Encoder presents at its output.
        
        As you can see, the VQVAE class is derived from the parent class Autoencoder.  Bulk of the
        computing in VQVAE is done through the functionality packed into the Autoencoder class.
        Therefore, in order to fully understand the VQVAE implementation here, your starting point
        should be the code for the Autoencoder class.  

        Note that the VQVAE code presented here is still tentative.  Most of the heavy lifting
        at the moment is done by the two Vector Representation classes I have borrowed from
        "zalandoresearch" at GitHub:

                  https://github.com/zalandoresearch/pytorch-vq-vae

        Class Path:   DLStudio  ->  VQVAE
        """  
        def __init__(self, dl_studio, encoder_in_im_size,  encoder_out_im_size, decoder_out_im_size, encoder_out_ch, num_repeats, num_codebook_vecs,
            codebook_vec_dim, commitment_cost, decay, path_saved_encoder, path_saved_decoder, path_saved_vector_quantizer, path_saved_prevq_and_postvq_convos ):
            super(DLStudio.VQVAE, self).__init__( dl_studio, encoder_in_im_size, encoder_out_im_size, decoder_out_im_size, encoder_out_ch, num_repeats, path_saved_model=None )
            self.parent_encoder =  DLStudio.Autoencoder.EncoderForAutoenc(dl_studio, encoder_in_im_size, encoder_out_im_size, encoder_out_ch, num_repeats, skip_connections=True) 
            self.parent_decoder =  DLStudio.Autoencoder.DecoderForAutoenc(dl_studio, encoder_out_im_size, decoder_out_im_size)
            self.num_codebook_vecs  = num_codebook_vecs
            self.codebook_vec_dim = codebook_vec_dim
            self.commitment_cost = commitment_cost
            self.decay = decay
            self.vqvae_encoder =  DLStudio.VQVAE.VQVaeEncoder(self.parent_encoder)      
            self.vqvae_decoder =  DLStudio.VQVAE.VQVaeDecoder(self.parent_decoder, encoder_out_im_size, encoder_out_ch)
            self.vector_quantizer = DLStudio.VQVAE.VectorQuantizerEMA(num_codebook_vecs, codebook_vec_dim, commitment_cost, decay)
            self.pre_vq_convo  =  nn.Conv2d(in_channels=encoder_out_ch, out_channels=codebook_vec_dim, kernel_size=1, stride=1)
            self.post_vq_convo =  nn.Conv2d(in_channels=encoder_out_ch, out_channels=codebook_vec_dim, kernel_size=1, stride=1)
            self.encoder_out_im_size = self.encoder.encoder_out_im_size
            self.encoder_out_ch  =  self.encoder.encoder_out_ch
            self.path_saved_encoder = path_saved_encoder
            self.path_saved_decoder = path_saved_decoder
            self.path_saved_vector_quantizer = path_saved_vector_quantizer
            self.path_saved_prevq_and_postvq_convos = path_saved_prevq_and_postvq_convos

        ##  These getter methods for the the subclass VQGAN that is derived from VQVQE:
        def get_vqvae_encoder(self):
            return self.vqvae_encoder 
        def get_vqvae_decoder(self):
            return self.vqvae_decoder 
        def get_vector_quantizer(self):      
            return self.vector_quantizer
        def get_pre_vq_convo(self):
            return self.pre_vq_convo
        def get_post_vq_convo(self):
            return self.post_vq_convo


        class VQVaeEncoder(nn.Module):
            """
            I'll use the same Encoder that is in VQVAE's parent class Autoencoder. 

            Class Path:   DLStudio  ->  VQVAE  ->  VQVaeEncoder
            """
            def __init__(self, parent_encoder):
                super(DLStudio.VQVAE.VQVaeEncoder, self).__init__()
                self.parent_encoder = parent_encoder

            def forward(self, x):
               encoded = self.parent_encoder(x)
               return encoded


        class VQVaeDecoder(nn.Module):
            """
            I'll use the same Decoder that is in VQVAE's parent class Autoencoder.

            Class Path:   DLStudio  ->  VQVAE  ->  VQVaeDecoder
            """
            def __init__(self, parent_decoder, encoder_out_im_size, encoder_out_ch):
                super(DLStudio.VQVAE.VQVaeDecoder, self).__init__()
                self.parent_decoder = parent_decoder
                self.encoder_out_im_size = encoder_out_im_size
                self.encoder_out_ch = encoder_out_ch

            def forward(self, quantized):
                decoded = self.parent_decoder( quantized.view(-1, self.encoder_out_ch, self.encoder_out_im_size[0], self.encoder_out_im_size[1]) )
                return decoded


        class VectorQuantizer(nn.Module):
            """
            This class is from:

                      https://github.com/zalandoresearch/pytorch-vq-vae

            This is an implementation of VQ-VAE by Aäron van den Oord et al. 

            Class Path:   DLStudio  ->  VQVAE  ->  VectorQuantizer
            """

            @static_var("_codebook", None) 
            def __init__(self, num_codebook_vecs, codebook_vec_dim, commitment_cost):
                super(DLStudio.VQVAE.VectorQuantizer, self).__init__()                
                self._codebook_vec_dim = codebook_vec_dim
                self._num_codebook_vecs = num_codebook_vecs
                
                self._codebook = nn.Embedding(self._num_codebook_vecs, self._codebook_vec_dim)
                self._codebook.weight.data.uniform_(-1/self._num_codebook_vecs, 1/self._num_embeddings)
                self._commitment_cost = commitment_cost
        
            def forward(self, inputs):
                # convert inputs from BCHW -> BHWC
                inputs = inputs.permute(0, 2, 3, 1).contiguous()               ## Reshaping the output of the Encoder since the
                                                                               ##   channel axis is going to be treated as the
                                                                               ##   embedding axis.
                input_shape = inputs.shape                                     ## Needed later for shape restoration with unflattening 
                # Flatten input
                flat_input = inputs.view(-1, self._codebook_vec_dim)
                # Calculate distances between the input embedding vector and each of the codebook vectors
                distances = (torch.sum(flat_input**2, dim=1, keepdim=True) + torch.sum(self._codebook.weight**2, dim=1)
                                                                              - 2 * torch.matmul(flat_input, self._codebook.weight.t()))
                # Encoding
                encoding_indices = torch.argmin(distances, dim=1).unsqueeze(1)
                encodings = torch.zeros(encoding_indices.shape[0], self._num_codebook_vecs, device=inputs.device)
                encodings.scatter_(1, encoding_indices, 1)
                # Quantize and unflatten
                quantized = torch.matmul(encodings, self._codebook.weight).view(input_shape)
                # Loss
                e_latent_loss = F.mse_loss(quantized.detach(), inputs)     
                q_latent_loss = F.mse_loss(quantized, inputs.detach())     
                loss = q_latent_loss + self._commitment_cost * e_latent_loss
                
                quantized = inputs + (quantized - inputs).detach()
                avg_probs = torch.mean(encodings, dim=0)
                perplexity = torch.exp(-torch.sum(avg_probs * torch.log(avg_probs + 1e-10)))
                
                # convert quantized from BHWC -> BCHW
                return loss, quantized.permute(0, 3, 1, 2).contiguous(), perplexity, encodings
        
        
        class VectorQuantizerEMA(nn.Module):
            """
            This class is from:

                      https://github.com/zalandoresearch/pytorch-vq-vae

            This is an implementation by Dominic Rampas of the VQ-VAE by Aäron van den Oord et al. 

            Class Path:   DLStudio  ->  VQVAE  ->  VectorQuantizerEMA
            """  
            static_codebook = {}
            def __init__(self, num_codebook_vecs, codebook_vec_dim, commitment_cost, decay, epsilon=1e-5):
                super(DLStudio.VQVAE.VectorQuantizerEMA, self).__init__()                
                self._codebook_vec_dim = codebook_vec_dim
                self._num_codebook_vecs = num_codebook_vecs
                DLStudio.VQVAE.VectorQuantizerEMA.static_codebook = nn.Embedding(self._num_codebook_vecs, self._codebook_vec_dim)
                self._codebook = DLStudio.VQVAE.VectorQuantizerEMA.static_codebook
                self._codebook.weight.data.normal_()
                self._commitment_cost = commitment_cost
                self.register_buffer('_ema_cluster_size', torch.zeros(num_codebook_vecs))
                self._ema_w = nn.Parameter(torch.Tensor(num_codebook_vecs, self._codebook_vec_dim))
                self._ema_w.data.normal_()
                self._decay = decay
                self._epsilon = epsilon
        
            def forward(self, inputs):
                # convert inputs from BCHW -> BHWC
                inputs = inputs.permute(0, 2, 3, 1).contiguous()                 ## Reshaping the output of the Encoder since the
                                                                                 ##   channel axis is going to be treated as the
                                                                                 ##   embedding axis.
                input_shape = inputs.shape                                       ## Needed later for shape restoration with unflattening 
                # Flatten input
                flat_input = inputs.view(-1, self._codebook_vec_dim)
                # Calculate distances
                distances = (torch.sum(flat_input**2, dim=1, keepdim=True) 
                            + torch.sum(self._codebook.weight**2, dim=1)
                            - 2 * torch.matmul(flat_input, self._codebook.weight.t()))
                # Encoding
                encoding_indices = torch.argmin(distances, dim=1).unsqueeze(1)
                ##  dimensionality num_emeddings
                encodings = torch.zeros(encoding_indices.shape[0], self._num_codebook_vecs, device=inputs.device)

                encodings.scatter_(1, encoding_indices, 1)    
                # Quantize and unflatten
                quantized = torch.matmul(encodings, self._codebook.weight).view(input_shape)
                if self.training:
                    self._ema_cluster_size = self._ema_cluster_size * self._decay +  (1 - self._decay) * torch.sum(encodings, 0)
                    # Laplace smoothing of the cluster size
                    n = torch.sum(self._ema_cluster_size.data)
                    self._ema_cluster_size = ( (self._ema_cluster_size + self._epsilon) / (n + self._num_codebook_vecs * self._epsilon) * n)
                    dw = torch.matmul(encodings.t(), flat_input)
                    self._ema_w = nn.Parameter(self._ema_w * self._decay + (1 - self._decay) * dw)
                    self._codebook.weight = nn.Parameter(self._ema_w / self._ema_cluster_size.unsqueeze(1))
                # Loss
                e_latent_loss = F.mse_loss(quantized.detach(), inputs)    
                loss = self._commitment_cost * e_latent_loss
                # Straight Through Estimator
                quantized = inputs + (quantized - inputs).detach()
                ##  this histogram will be flat.
                avg_probs = torch.mean(encodings, dim=0)
                perplexity = torch.exp(-torch.sum(avg_probs * torch.log(avg_probs + 1e-10)))  
                # convert quantized from BHWC -> BCHW
                return loss, quantized.permute(0, 3, 1, 2).contiguous(), perplexity, encodings

        
        def save_encoder_model(self, model):
            '''
            Save the trained Encoder model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_encoder)

        def save_decoder_model(self, model):
            '''
            Save the trained Decoder model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_decoder)

        def save_vector_quantizer_model(self, model):
            '''
            Save the trained Vector Quantizer model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_vector_quantizer)

        def save_prevq_and_postvq_convos(self, prevq_convo, postvq_convo):
            convo_dict =  {"prevq" : prevq_convo,  "postvq" : postvq_convo}
            torch.save( convo_dict, self.path_saved_prevq_and_postvq_convos )


        def run_code_for_training_VQVAE( self, vqvae, display_train_loss=False ):
            """
            The code for set_dataloaders() for the VAE class shows how the overall dataset of images is divided into
            training and testing subsets.  
            """            
            vqvae_encoder = vqvae.vqvae_encoder.to(self.dl_studio.device)
            vqvae_vector_quantizer =  vqvae.vector_quantizer.to(self.dl_studio.device)
            vqvae_decoder = vqvae.vqvae_decoder.to(self.dl_studio.device)
            pre_vq_convo = vqvae.pre_vq_convo.to(self.dl_studio.device)
            post_vq_convo = vqvae.post_vq_convo.to(self.dl_studio.device)

            accum_times = []
            start_time = time.perf_counter()
            print("")
            batch_size = self.dl_studio.batch_size
            print("\n\n batch_size: ", batch_size)
            num_batches_in_data_source = len(self.train_dataloader)
            total_num_updates = self.dl_studio.epochs * num_batches_in_data_source
            print("\n\n number of batches in the dataset: ", num_batches_in_data_source)
            optimizer1 = optim.Adam(vqvae_encoder.parameters(), lr=self.dl_studio.learning_rate)     
            optimizer2 = optim.Adam(vqvae_decoder.parameters(), lr=self.dl_studio.learning_rate)     
            optimizer3 = optim.Adam(vqvae_vector_quantizer.parameters(), lr=self.dl_studio.learning_rate)     
            optimizer4 = optim.Adam(pre_vq_convo.parameters(), lr=self.dl_studio.learning_rate)     
            optimizer5 = optim.Adam(post_vq_convo.parameters(), lr=self.dl_studio.learning_rate)     

            training_loss_tally = []
            perplexity_tally = []        
            data_variance = 0.0
            for epoch in range(self.dl_studio.epochs):                                                              
                print("")
                running_loss = 0.0
                running_perplexity = 0.0
                for i, data in enumerate(self.train_dataloader):                                    
                    input_images, _ = data                              
                    input_images = input_images.to(self.dl_studio.device)
                    optimizer1.zero_grad()
                    optimizer2.zero_grad()
                    optimizer3.zero_grad()
                    optimizer4.zero_grad()
                    optimizer5.zero_grad()

                    z = vqvae_encoder(input_images)
                    z = pre_vq_convo(z)
                    vq_loss, quantized, perplexity, _ =  vqvae_vector_quantizer(z)
                    z = post_vq_convo(quantized)
                    decoder_out = vqvae_decoder(z)

                    recon_loss = nn.MSELoss(reduction='sum')( input_images, decoder_out ) 
                    loss = recon_loss + vq_loss
                    loss.backward()                                                                                        
                    optimizer1.step()
                    optimizer2.step()
                    optimizer3.step()
                    optimizer4.step()
                    optimizer5.step()

                    running_loss += loss
                    running_perplexity += perplexity
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        avg_perplexity = running_perplexity / float(200)                        
                        training_loss_tally.append(avg_loss.item())
                        perplexity_tally.append(avg_perplexity.item())
                        running_loss = 0.0
                        running_perplexity = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%2d/%2d  i:%4d  elapsed_time: %4d secs]   loss: %10.6f         perplexity: %10.6f " % 
                                                             (epoch+1, self.dl_studio.epochs, i+1, time_elapsed, avg_loss, avg_perplexity)) 
                        accum_times.append(current_time-start_time)
            print("\nFinished Training VQVAE\n")
            self.save_encoder_model( vqvae_encoder )
            self.save_decoder_model( vqvae_decoder )
            self.save_vector_quantizer_model( vqvae_vector_quantizer )
            self.save_prevq_and_postvq_convos(pre_vq_convo, post_vq_convo)
            fig, (ax1,ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12,5))
            ax1.plot(training_loss_tally)
            ax2.plot(perplexity_tally)                                  
            ax1.set_xticks(np.arange(total_num_updates // 200))    ## since each val for plotting is generated every 200 iterations
            ax2.set_xticks(np.arange(total_num_updates // 200))
            ax1.set_xlabel("iterations") 
            ax2.set_xlabel("iterations") 
            ax1.set_ylabel("vqvae training loss") 
            ax2.set_ylabel("vqvae Perplexity") 
            plt.savefig("vqvae_training_losses_and_perplexity.png")
            plt.show()


        def run_code_for_evaluating_VQVAE(self, vqvae, visualization_dir = "vqvae_visualization_dir" ):
            """
            The main point here is to use the co-called "unseen images" for evaluating the
            performance of VQVAE.  If you look at the set_dataloader() function for the VAE
            class, you will see me setting aside a certain number of the available images for
            testing.  These randomly chosen images play NO role in training.
            """
            if os.path.exists(visualization_dir):  
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   
     
            vqvae_encoder = vqvae.vqvae_encoder.eval()
            vqvae_decoder = vqvae.vqvae_decoder.eval()
            vqvae_vector_quantizer = vqvae.vector_quantizer.eval()

            convo_dict = torch.load(self.path_saved_prevq_and_postvq_convos)
            pre_vq_convo = convo_dict["prevq"]
            post_vq_convo = convo_dict["postvq"]
            pre_vq_convo   =  vqvae.pre_vq_convo.eval()
            post_vq_convo   =  vqvae.post_vq_convo.eval()

            vqvae_encoder.load_state_dict(torch.load(self.path_saved_encoder))
            vqvae_decoder.load_state_dict(torch.load(self.path_saved_decoder))
            vqvae_vector_quantizer.load_state_dict(torch.load(self.path_saved_vector_quantizer))
            vqvae_encoder.to(self.dl_studio.device) 
            vqvae_decoder.to(self.dl_studio.device)
            vqvae_vector_quantizer.to(self.dl_studio.device)
            pre_vq_convo.to(self.dl_studio.device)
            post_vq_convo.to(self.dl_studio.device)

            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):                                    
                    print("\n\n\n=========Showing VQVAE results for test batch %d===============" % i)
                    test_images, _ = data     
                    test_images = test_images.to(self.dl_studio.device)

                    z = vqvae_encoder(test_images)
                    z = pre_vq_convo(z)
                    _, quantized, perplexity, _ =  vqvae_vector_quantizer(z)
                    z = post_vq_convo(quantized)
                    decoder_out = vqvae_decoder(z)

                    decoder_out  =  ( decoder_out - decoder_out.min() ) / ( decoder_out.max() -  decoder_out.min() )
                    together = torch.zeros( test_images.shape[0], test_images.shape[1], test_images.shape[2], 2 * test_images.shape[3], dtype=torch.float )
                    together[:,:,:,0:test_images.shape[3]]  =  test_images
                    together[:,:,:,test_images.shape[3]:]  =   decoder_out 
                    plt.figure(figsize=(40,20))
                    plt.imshow(np.transpose(torchvision.utils.make_grid(together.cpu(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                    plt.title("VQVAE Output Images for iteration %d" % i)
                    plt.savefig(visualization_dir + "/vqvae_decoder_out_%s" % str(i) + ".png")
                    plt.show()


        def set_dataloader(self):
            """
            Note the call to random_split() in the second statement for dividing the overall dataset of images into 
            two DISJOINT parts, one for training and the other for testing.  Since my evaluation of the VAE at this
            time is purely on the basis of the visual quality of the output of the Decoder, I have set aside only
            200 randomly chosen images for testing.  Ordinarily, through, you would want to split the dataset in 
            the 70:30 or 80:20 ratio for training and testing.
            """
            dataset = torchvision.datasets.ImageFolder(root=self.dl_studio.dataroot,       
                           transform = tvt.Compose([                 
                                                tvt.Resize(self.dl_studio.image_size),             
                                                tvt.CenterCrop(self.dl_studio.image_size),         
                                                tvt.ToTensor(),                     
                                                tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),         
                           ]))
            dataset_train, dataset_test  =  torch.utils.data.random_split( dataset, lengths = [len(dataset) - 200, 200])
            self.train_dataloader = torch.utils.data.DataLoader(dataset_train, batch_size=self.dl_studio.batch_size, shuffle=True, num_workers=4)
            self.test_dataloader = torch.utils.data.DataLoader(dataset_test, batch_size=self.dl_studio.batch_size, shuffle=True, num_workers=4)



    ###%%%
    #####################################################################################################################
    ######################################  Start Definition of Inner Class VQGAN  ######################################

    class VQGAN (VQVAE):             

        def __init__(self, dl_studio, encoder_in_im_size,  encoder_out_im_size, decoder_out_im_size, encoder_out_ch, num_repeats, num_codebook_vecs, 
              codebook_vec_dim, commitment_cost, decay, perceptual_loss_factor, use_patch_gan_logic, path_saved_generator):
            super(DLStudio.VQGAN, self).__init__( dl_studio, encoder_in_im_size,  encoder_out_im_size, decoder_out_im_size, encoder_out_ch,
                                                                  num_repeats, num_codebook_vecs, codebook_vec_dim, commitment_cost, decay,
                              path_saved_encoder=None, path_saved_decoder=None, path_saved_vector_quantizer=None, path_saved_prevq_and_postvq_convos=None)
            self.num_codebook_vecs  = num_codebook_vecs
            self.codebook_vec_dim = codebook_vec_dim
            self.commitment_cost = commitment_cost
            self.decay = decay
            self.perceptual_loss_factor = perceptual_loss_factor
            self.vqgan_encoder =  super(DLStudio.VQGAN, self).get_vqvae_encoder()
            self.vqgan_decoder =  super(DLStudio.VQGAN, self).get_vqvae_decoder()
            self.vqgan_vector_quantizer =  super(DLStudio.VQGAN, self).get_vector_quantizer()
            self.vqgan_pre_vq_convo = super(DLStudio.VQGAN, self).get_pre_vq_convo()
            self.vqgan_post_vq_convo = super(DLStudio.VQGAN, self).get_post_vq_convo()
            self.discriminator = DLStudio.VQGAN.Discriminator_PatchGAN() if use_patch_gan_logic else DLStudio.VQGAN.Discriminator()
            self.path_saved_generator = path_saved_generator
            self.codebook = super(DLStudio.VQGAN, self).VectorQuantizerEMA.static_codebook

        class Discriminator(nn.Module):
            """
            This is for the non-patchGAN case.

            This is an implementation of the DCGAN Discriminator. I refer to the DCGAN network topology as
            the 4-2-1 network.  Each layer of the Discriminator network carries out a strided
            convolution with a 4x4 kernel, a 2x2 stride and a 1x1 padding for all but the final
            layer. The output of the final convolutional layer is pushed through a sigmoid to yield
            a scalar value as the final output for each image in a batch.
    
            Class Path:  DLStudio  ->   VQGAN  ->  Discriminator
            """
            def __init__(self):
                super(DLStudio.VQGAN.Discriminator, self).__init__()
                self.conv_in = nn.Conv2d(  3,    64,      kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in2 = nn.Conv2d( 64,   128,     kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in3 = nn.Conv2d( 128,  256,     kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in4 = nn.Conv2d( 256,  512,     kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in5 = nn.Conv2d( 512,  1,       kernel_size=4,      stride=1,    padding=0, bias=False)
                self.bn1  = nn.BatchNorm2d(128)
                self.bn2  = nn.BatchNorm2d(256)
                self.bn3  = nn.BatchNorm2d(512)
                self.sig = nn.Sigmoid()
    
            def forward(self, x):                 
                x = torch.nn.functional.leaky_relu(self.conv_in(x), negative_slope=0.2, inplace=True)
                x = self.bn1(self.conv_in2(x))
                x = torch.nn.functional.leaky_relu(x, negative_slope=0.2, inplace=True)
                x = self.bn2(self.conv_in3(x))
                x = torch.nn.functional.leaky_relu(x, negative_slope=0.2, inplace=True)
                x = self.bn3(self.conv_in4(x))
                x = torch.nn.functional.leaky_relu(x, negative_slope=0.2, inplace=True)
                x = self.conv_in5(x)
                x = self.sig(x)
                return x


        class Discriminator_PatchGAN(nn.Module):
            """
            This is a slight variation of the Discriminator by Dominic Rampas:

                      https://github.com/zalandoresearch/pytorch-vq-vae

            Class Path:  DLStudio  ->   VQGAN  ->  Discriminator_PatchGAN
            """
            def __init__(self):
                super(DLStudio.VQGAN.Discriminator_PatchGAN, self).__init__()
                num_filters_last = 128
                n_layers = 3
                layers = [nn.Conv2d(3, num_filters_last, 4, 2, 1), nn.LeakyReLU(0.2)]
                num_filters_mult = 1
        
                for i in range(1, n_layers + 1):
                    num_filters_mult_last = num_filters_mult
                    num_filters_mult = min(2 ** i, 8)
                    layers += [
                        nn.Conv2d(num_filters_last * num_filters_mult_last, num_filters_last * num_filters_mult, 4,
                                  2 if i < n_layers else 3, 3, bias=False),
                        nn.BatchNorm2d(num_filters_last * num_filters_mult),
                        nn.LeakyReLU(0.2, True)
                    ]
        
                layers.append(nn.Conv2d(num_filters_last * num_filters_mult, 1, 4, 1, 1))
                self.model = nn.Sequential(*layers)
            def forward(self, x):
                return nn.Sigmoid()( self.model(x) )
        


        class Discriminator_PatchGAN_2(nn.Module):
            """
            This Discriminator is from DLStudio's AdversarialLearning module.  
 
            Class Path:  DLStudio  ->   VQGAN  ->  Discriminator_PatchGAN
            """
            def __init__(self):
                super(DLStudio.VQGAN.Discriminator_PatchGAN, self).__init__()
                self.conv_in = nn.Conv2d(  3,    64,      kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in2 = nn.Conv2d( 64,   128,     kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in3 = nn.Conv2d( 128,  256,     kernel_size=4,      stride=2,    padding=1, bias=False)
                self.conv_in5 = nn.Conv2d( 256,  1,       kernel_size=5,      stride=1,    padding=0, bias=False)
                self.bn1  = nn.BatchNorm2d(128)
                self.bn2  = nn.BatchNorm2d(256)
                self.sig = nn.Sigmoid()
    
            def forward(self, x):                 
                x = torch.nn.functional.leaky_relu(self.conv_in(x), negative_slope=0.2, inplace=True)
                x = self.bn1(self.conv_in2(x))
                x = torch.nn.functional.leaky_relu(x, negative_slope=0.2, inplace=True)
                x = self.bn2(self.conv_in3(x))
                x = torch.nn.functional.leaky_relu(x, negative_slope=0.2, inplace=True)
                x = self.conv_in5(x)
                x = self.sig(x)
                return x


        def save_generator_model(self, model):
            '''
            Save the trained Generator (meanin, VQGAN) model to a disk file
            '''
            torch.save(model.state_dict(), self.path_saved_generator)

        def weights_init(self, m):        
            """
            Uses the DCGAN initializations for the weights
            """
            classname = m.__class__.__name__     
            if classname.find('Conv') != -1:         
                nn.init.normal_(m.weight.data, 0.0, 0.02)      
            elif classname.find('BatchNorm') != -1:         
                nn.init.normal_(m.weight.data, 1.0, 0.02)       
                nn.init.constant_(m.bias.data, 0)      

        def run_code_for_training_VQGAN( self, vqgan ):
            """
            This uses the regular Discriminator.  That is, the Discriminator puts out A SINGLE SCALAR VALUE that
            expresses the probability that the image at its input came from the probability distribution that
            describes the training dataset.

            IMPORTANT:  You will get significantly better results if you train with the next function named

                                       run_code_for_PATCH_BASED_training_VQGAN

            Also note that the code for set_dataloaders() for the VAE class shows how the overall dataset of 
            images is divided into training and testing subsets.  
            """            
            def normed_tensor(x):
                norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
                return x / (norm_factor + 1e-10)

            class Generator(nn.Module):
                """
                In keeping with the ethos of Adversarial Learning, it's good to bundle the code so that there
                is readily identifiable separation between the Generator part and the Discriminator part.  In 
                our case, the Generator is the VQGAN network itself.
                """
                def __init__(self):
                    super(Generator, self).__init__()
                    self.vqgan_encoder = vqgan.vqgan_encoder
                    self.vqgan_vector_quantizer =  vqgan.vector_quantizer
                    self.vqgan_decoder = vqgan.vqgan_decoder
                    self.pre_vq_convo = vqgan.vqgan_pre_vq_convo
                    self.post_vq_convo = vqgan.vqgan_post_vq_convo

                def forward(self, input_images):      
                    z = self.vqgan_encoder(input_images)
                    z = self.pre_vq_convo(z)
                    vq_loss, quantized, perplexity, _ =  self.vqgan_vector_quantizer(z)
                    z = self.post_vq_convo(quantized)
                    decoder_out = self.vqgan_decoder(z)
                    decoder_out = normed_tensor(decoder_out)
                    return decoder_out, perplexity, vq_loss

            generator = Generator().to(self.dl_studio.device)
            print("\n\nType of generator constructed: ", type(generator))
            print("number of learnable params in generator: ", sum(p.numel() for p in generator.parameters() if p.requires_grad))
            self.generator = generator
            discriminator = vqgan.discriminator.to(self.dl_studio.device)
            discriminator.apply(self.weights_init)
            generator.apply(self.weights_init)
            print("number of learnable params in discriminator: ", sum(p.numel() for p in discriminator.parameters() if p.requires_grad))
            lpips = LearnedPerceptualImagePatchSimilarity(net_type='vgg').to(self.dl_studio.device)
            accum_times = []
            start_time = time.perf_counter()
            print("")
            batch_size = self.dl_studio.batch_size
            print("\n\n batch_size: ", batch_size)
            num_batches_in_data_source = len(self.train_dataloader)
            total_num_updates = self.dl_studio.epochs * num_batches_in_data_source
            print("\n\n number of batches in the dataset: ", num_batches_in_data_source)
            optimizer1 = optim.Adam(generator.parameters(), lr=self.dl_studio.learning_rate)
            optimizer2 = optim.Adam(discriminator.parameters(), lr=self.dl_studio.learning_rate)     
            disc_loss_reals_tally = []
            disc_loss_fakes_tally = []
            generator_loss_tally = []
            perplexity_tally = []        
            real_label = 1      ##  Will be used as target when the Discriminator is trained on the dataset images
            fake_label = 0      ##  Will be used as target when the Discriminator is fed the output of the "Generator" --- meaning the VQGAN
            for epoch in range(self.dl_studio.epochs):                                                              
                print("")
                running_disc_loss_reals =  running_disc_loss_fakes = running_generator_loss = running_perplexity =  0.0

                for i, data in enumerate(self.train_dataloader):                                    
                    input_images, _ = data                              
                    input_images = input_images.to(self.dl_studio.device)
                    input_images = normed_tensor(input_images)
                    optimizer1.zero_grad()             ## generator
                    optimizer2.zero_grad()             ## discriminator
                    ##  Maximization for Discriminator training --- Part 1:
                    ##
                    ##  Maximization-Part 1 means that we want the output of the Discrminator to be as large as possible, 
                    ##  meaning to be as close to 1.0 as possible when it sees the training images.  The Discriminator outputs 
                    ##  the prob that an image came from the same distribution as the training dataset. The larger this prob,
                    ##  the smaller the BCELoss:
                    targets = torch.full((input_images.shape[0],), real_label, dtype=torch.float, device=self.dl_studio.device)  
                    output_disc_reals = discriminator(input_images).view(-1)     ## Discriminaotor should produce a scalar for each im in batch
                    lossD_for_reals = nn.BCELoss()(output_disc_reals, targets)                                                   

                    ##  Maximization for Discriminator training --- Part 2:
                    ##
                    targets = torch.full((input_images.shape[0],), fake_label, dtype=torch.float, device=self.dl_studio.device)  
                    targets = targets.float().to(self.dl_studio.device)
                    decoder_out, perplexity, vq_loss = generator(input_images)
                    output_disc_fakes = discriminator(decoder_out).view(-1)        ## Discriminaotor should produce a scalar for each im in batch
                    lossD_for_fakes = nn.BCELoss()(output_disc_fakes.detach().view(-1), targets)    ##  NOTE: invocation of detach() on generator
                    discriminator_loss  =   lossD_for_reals + lossD_for_fakes
                    discriminator_loss.backward()
                    ## Only the Discriminator params will be update
                    optimizer2.step()

                    ##  Minimization for Generator training
                    ##
                    targets = torch.full((input_images.shape[0],), real_label, dtype=torch.float, device=self.dl_studio.device)  
                    lossG_for_fakes = nn.BCELoss()(output_disc_fakes, targets)                                                   
                    recon_loss = nn.MSELoss()( input_images, decoder_out ) 
                    perceptual_loss = lpips( normed_tensor(input_images), normed_tensor(decoder_out) )
                    generator_loss  =  recon_loss +  lossG_for_fakes + vq_loss  + self.perceptual_loss_factor * perceptual_loss     
                    generator_loss.backward()
                    ## Only the VQGAN params (the Generator) will be updated:

                    optimizer1.step()
                    running_disc_loss_reals += lossD_for_reals
                    running_disc_loss_fakes += lossD_for_fakes
                    running_perplexity += perplexity
                    running_generator_loss += generator_loss
                    if i % 200 == 199:    
                        avg_gen_loss = running_generator_loss / float(200)
                        avg_disc_loss_reals = running_disc_loss_reals / float(200)
                        avg_disc_loss_fakes = running_disc_loss_fakes / float(200)
                        avg_perplexity = running_perplexity / float(200)                        
                        generator_loss_tally.append(avg_gen_loss.item())
                        disc_loss_reals_tally.append(avg_disc_loss_reals.item())
                        disc_loss_fakes_tally.append(avg_disc_loss_fakes.item())
                        perplexity_tally.append(avg_perplexity.item())
                        running_disc_loss_reals = running_disc_loss_fakes = running_generator_loss = running_perplexity = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%2d/%2d  i:%4d  elapsed_time: %4d secs]   disc_loss_reals: %8.6f   disc_loss_fakes: %8.6f   gen_loss:  %8.6f   perplexity: %8.6f " %  (epoch+1, self.dl_studio.epochs, i+1, time_elapsed,                    avg_disc_loss_reals, avg_disc_loss_fakes, avg_gen_loss, avg_perplexity)) 
                        accum_times.append(current_time-start_time)
                torch.save(generator.state_dict(), "checkpoint_dir/checkpoint_" +  str(epoch))
                torch.save(self.codebook.state_dict(), "codebooks_saved/codebook_" +  str(epoch))
            print("\nFinished Training VQGAN\n")
            self.save_generator_model( generator )
            fig, (ax1,ax2,ax3,ax4) = plt.subplots(nrows=1, ncols=4, figsize=(20,5))
            ax1.plot(disc_loss_reals_tally)
            ax2.plot(disc_loss_fakes_tally)
            ax3.plot(generator_loss_tally)
            ax4.plot(perplexity_tally)                                  
            ax1.set_xticks(np.arange(total_num_updates // 200))    ## since each val for plotting is generated every 200 iterations
            ax2.set_xticks(np.arange(total_num_updates // 200))
            ax3.set_xticks(np.arange(total_num_updates // 200))
            ax4.set_xticks(np.arange(total_num_updates // 200))
            ax1.set_xlabel("iterations") 
            ax2.set_xlabel("iterations") 
            ax3.set_xlabel("iterations") 
            ax4.set_xlabel("iterations") 
            ax1.set_ylabel("discriminator loss - reals") 
            ax2.set_ylabel("discriminator loss - fakes") 
            ax3.set_ylabel("generator loss") 
            ax4.set_ylabel("vqgan Perplexity") 
            plt.savefig("vqgan_training_losses_and_perplexity.png")
            plt.show()


        def run_code_for_PATCH_BASED_training_VQGAN( self, vqgan ):
            """
            This is based on the patchGAN based Discriminator.  That is, the Discriminator assumes that the input
            image can be thought of as being composed of an NxN array of patches.  Subsequently, it puts out an
            NxN array of probability numbers, with each number expressing the belief that it came from the same
            probability distribution that defines the training dataset of images.

            The code for set_dataloaders() for the VAE class shows how the overall dataset of images is divided into
            training and testing subsets.  
            """            
            def normed_tensor(x):
                norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
                return x / (norm_factor + 1e-10)

            class Generator(nn.Module):
                def __init__(self):
                    super(Generator, self).__init__()
                    self.vqgan_encoder = vqgan.vqgan_encoder
                    self.vqgan_vector_quantizer =  vqgan.vector_quantizer
                    self.vqgan_decoder = vqgan.vqgan_decoder
                    self.pre_vq_convo = vqgan.vqgan_pre_vq_convo
                    self.post_vq_convo = vqgan.vqgan_post_vq_convo
                def forward(self, input_images):      
                    z = self.vqgan_encoder(input_images)
                    z = self.pre_vq_convo(z)
                    vq_loss, quantized, perplexity, encoding_indices =  self.vqgan_vector_quantizer(z)
                    z = self.post_vq_convo(quantized)
                    decoder_out = self.vqgan_decoder(z)
                    decoder_out = normed_tensor(decoder_out)
                    return decoder_out, perplexity, vq_loss, encoding_indices

            self.codebook = super(DLStudio.VQGAN, self).VectorQuantizerEMA.static_codebook
            generator = Generator().to(self.dl_studio.device)
            print("\n\nType of generator constructed: ", type(generator))
            print("number of learnable params in generator: ", sum(p.numel() for p in generator.parameters() if p.requires_grad))
            self.generator = generator
            discriminator = vqgan.discriminator.to(self.dl_studio.device)
            discriminator.apply(self.weights_init)
            generator.apply(self.weights_init)
            print("number of learnable params in discriminator: ", sum(p.numel() for p in discriminator.parameters() if p.requires_grad))
            lpips = LearnedPerceptualImagePatchSimilarity(net_type='vgg').to(self.dl_studio.device)
            accum_times = []
            start_time = time.perf_counter()
            print("")
            batch_size = self.dl_studio.batch_size
            print("\n\n batch_size: ", batch_size)
            num_batches_in_data_source = len(self.train_dataloader)
            total_num_updates = self.dl_studio.epochs * num_batches_in_data_source
            print("\n\n number of batches in the dataset: ", num_batches_in_data_source)
            optimizer1 = optim.Adam(generator.parameters(), lr=self.dl_studio.learning_rate)
            optimizer2 = optim.Adam(discriminator.parameters(), lr=self.dl_studio.learning_rate)     
            disc_loss_reals_tally = []
            disc_loss_fakes_tally = []
            generator_loss_tally = []
            perplexity_tally = []        
            data_variance = 0.0
            for epoch in range(self.dl_studio.epochs):                                                              
                print("")
                running_disc_loss_reals =  running_disc_loss_fakes = running_generator_loss = running_perplexity =  0.0
                for i, data in enumerate(self.train_dataloader):                                    
                    input_images, _ = data                              
                    input_images = input_images.to(self.dl_studio.device)
                    input_images = normed_tensor(input_images)
                    optimizer1.zero_grad()             ## generator
                    optimizer2.zero_grad()             ## discriminator

                    ##  Maximization for Discriminator training --- Part 1:
                    ##
                    ##  Maximization-Part 1 means that we want the output of the Discrminator to be as large as possible, 
                    ##  meaning to be as close to 1.0 as possible when it sees the training images.  The Discriminator outputs 
                    ##  the prob that an image came from the same distribution as the training dataset. The larger this prob,
                    ##  the smaller the BCELoss:
                    targets = torch.ones( input_images.shape[0], 1, 4, 4 ).float().to(self.dl_studio.device)
                    output_disc_reals = discriminator(input_images)     ## Discriminaotor should produce a scalar for each im in batch
                    lossD_for_reals = nn.BCELoss()(output_disc_reals, targets)                                                   

                    ##  Maximization for Discriminator training --- Part 2:
                    ##
                    targets = torch.zeros( input_images.shape[0], 1, 4, 4 ).float().to(self.dl_studio.device)
                    if 'singlefile' in str(type(generator)):
                        decoder_out, vq_loss, encoding_indices = generator(input_images)   
                        perplexity = len(encoding_indices)
                    else:
                        decoder_out, perplexity, vq_loss, encoding_indices = generator(input_images)   
                    output_disc_fakes = discriminator(decoder_out)        ## Discriminaotor should produce a scalar for each im in batch
                    lossD_for_fakes = nn.BCELoss()(output_disc_fakes.detach(), targets)    ##  NOTE: invocation of detach() on generator
                    discriminator_loss  =   (lossD_for_reals + lossD_for_fakes).mean()
                    discriminator_loss.backward()
                    ## Only the Discriminator params will be update
                    optimizer2.step()

                    ##  Minimization for Generator training
                    ##
                    targets = torch.ones( input_images.shape[0], 1, 4, 4 ).float().to(self.dl_studio.device)
                    lossG_for_fakes = nn.BCELoss()(output_disc_fakes, targets)                                                   
                    recon_loss = nn.MSELoss()( input_images, decoder_out ) 
                    perceptual_loss = lpips( normed_tensor(input_images), normed_tensor(decoder_out) )
                    generator_loss  =  recon_loss +  lossG_for_fakes + vq_loss  + self.perceptual_loss_factor * perceptual_loss     
                    generator_loss.backward()
                    ## Only the VQGAN params (the Generator) will be updated:
                    optimizer1.step()

                    running_disc_loss_reals += lossD_for_reals
                    running_disc_loss_fakes += lossD_for_fakes
                    running_perplexity += perplexity
                    running_generator_loss += generator_loss
                    if i % 200 == 199:    
                        avg_gen_loss = running_generator_loss / float(200)
                        avg_disc_loss_reals = running_disc_loss_reals / float(200)
                        avg_disc_loss_fakes = running_disc_loss_fakes / float(200)
                        avg_perplexity = running_perplexity / float(200)                        

                        generator_loss_tally.append(avg_gen_loss.item())
                        disc_loss_reals_tally.append(avg_disc_loss_reals.item())
                        disc_loss_fakes_tally.append(avg_disc_loss_fakes.item())
                        if 'singlefile' in str(type(generator)):
                            perplexity_tally.append(avg_perplexity)
                        else:
                            perplexity_tally.append(avg_perplexity.item())
                        running_disc_loss_reals = running_disc_loss_fakes = running_generator_loss = running_perplexity = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%2d/%2d  i:%4d  elapsed_time: %4d secs]   disc_loss_reals: %8.6f   disc_loss_fakes: %8.6f   gen_loss:  %8.6f   perplexity: %8.6f " %  (epoch+1, self.dl_studio.epochs, i+1, time_elapsed, avg_disc_loss_reals, avg_disc_loss_fakes, avg_gen_loss, avg_perplexity))
                        accum_times.append(current_time-start_time)
                if epoch % 10 == 9:
                    torch.save(generator.state_dict(), "checkpoint_dir/generator_" +  str(epoch))
                    torch.save(self.codebook.state_dict(), "checkpoint_dir/codebook_" +  str(epoch))
                    torch.save(self.vqgan_encoder.state_dict(), "checkpoint_dir/vqgan_encoder_" +  str(epoch))
                    torch.save(self.vqgan_decoder.state_dict(), "checkpoint_dir/vqgan_decoder_" +  str(epoch))
                    torch.save(self.vqgan_vector_quantizer.state_dict(), "checkpoint_dir/vqgan_vector_quantizer_" +  str(epoch))
                    torch.save(self.vqgan_pre_vq_convo.state_dict(), "checkpoint_dir/vqgan_pre_vq_convo_" +  str(epoch))
                    torch.save(self.vqgan_post_vq_convo.state_dict(), "checkpoint_dir/vqgan_post_vq_convo_" +  str(epoch))

            print("\nFinished Training VQGAN\n")
            self.save_generator_model( generator )
            fig, (ax1,ax2,ax3,ax4) = plt.subplots(nrows=1, ncols=4, figsize=(20,5))
            ax1.plot(disc_loss_reals_tally)
            ax2.plot(disc_loss_fakes_tally)
            ax3.plot(generator_loss_tally)
            ax4.plot(perplexity_tally)                                  
            ax1.set_xticks(np.arange(total_num_updates // 200))    ## since each val for plotting is generated every 200 iterations
            ax2.set_xticks(np.arange(total_num_updates // 200))
            ax3.set_xticks(np.arange(total_num_updates // 200))
            ax4.set_xticks(np.arange(total_num_updates // 200))
            ax1.set_xlabel("iterations") 
            ax2.set_xlabel("iterations") 
            ax3.set_xlabel("iterations") 
            ax4.set_xlabel("iterations") 
            ax1.set_ylabel("discriminator loss - reals") 
            ax2.set_ylabel("discriminator loss - fakes") 
            ax3.set_ylabel("generator loss") 
            ax4.set_ylabel("vqgan Perplexity") 
            plt.savefig("vqgan_training_losses_and_perplexity.png")
            plt.show()


        def run_code_for_evaluating_VQGAN(self, vqgan, visualization_dir = "vqgan_visualization_dir" ):
            """
            The main point here is to use the co-called "unseen images" for evaluating the
            performance of VQGAN.  If you look at the set_dataloader() function for the VAE
            class, you will see me setting aside a certain number of the available images for
            testing.  These randomly chosen images play NO role in training.
            """
            if os.path.exists(visualization_dir):  
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   

            def normed_tensor(x):
                norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
                return x / (norm_factor + 1e-10)

            class Generator(nn.Module):
                def __init__(self):
                    super(Generator, self).__init__()
                    self.vqgan_encoder = vqgan.vqgan_encoder
                    self.vqgan_vector_quantizer =  vqgan.vector_quantizer
                    self.vqgan_decoder = vqgan.vqgan_decoder
                    self.pre_vq_convo = vqgan.vqgan_pre_vq_convo
                    self.post_vq_convo = vqgan.vqgan_post_vq_convo
                def forward(self, input_images):      
                    z = self.vqgan_encoder(input_images)
                    z = self.pre_vq_convo(z)
                    vq_loss, quantized, perplexity, encoding_indices =  self.vqgan_vector_quantizer(z)
                    z = self.post_vq_convo(quantized)
                    decoder_out = self.vqgan_decoder(z)
                    decoder_out = normed_tensor(decoder_out)
                    return decoder_out, perplexity, vq_loss, encoding_indices

            generator = Generator().to(self.dl_studio.device)
            generator.load_state_dict(torch.load(self.path_saved_generator))
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):                                    
                    print("\n\n\n=========Showing VQGAN results for test batch %d===============" % i)
                    test_images, _ = data     
                    test_images = test_images.to(self.dl_studio.device)
                    if 'singlefile' in str(type(generator)):
                        decoder_out, vq_loss, _ = generator(test_images)   
                    else:
                        decoder_out, _, vq_loss, _ = generator(test_images)   
                    decoder_out  =  ( decoder_out - decoder_out.min() ) / ( decoder_out.max() -  decoder_out.min() )
                    together = torch.zeros( test_images.shape[0], test_images.shape[1], test_images.shape[2], 2 * test_images.shape[3], dtype=torch.float )
                    together[:,:,:,0:test_images.shape[3]]  =  test_images
                    together[:,:,:,test_images.shape[3]:]  =   decoder_out 
                    plt.figure(figsize=(40,20))
                    plt.imshow(np.transpose(torchvision.utils.make_grid(together.cpu(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                    plt.title("VQGAN Output Images for iteration %d" % i)
                    plt.savefig(visualization_dir + "/vqgan_decoder_out_%s" % str(i) + ".png")
                    plt.show()
  

        def display_2_images( self, in_image, out_image ):
            """
            Will also work for a batch of images for the two arguments
            """
            out  =  ( out_image - out_image.min() ) / ( out_image.max() -  out_image.min() )
            together = torch.zeros( in_image.shape[0], in_image.shape[1], in_image.shape[2], 2 * in_image.shape[3], dtype=torch.float )
            together[:,:,:,0:in_image.shape[3]]  =  in_image
            together[:,:,:,in_image.shape[3]:]  =   out 
            plt.figure(figsize=(40,20))
            plt.imshow(np.transpose(torchvision.utils.make_grid(together.detach(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
            plt.title("Intermediate Input and Ouput Images")
            plt.savefig("intermediate_input_and_output_images.png")
            plt.show()


        @torch.no_grad()
        def encode_image_into_sequence_of_indices_to_codebook_vectors(self, im_name=None ):
            """
            im_name is the name of a file with a suffix like ".jpg", ".png", etc.

            When im_name is not supplied, the function produces the output for a batch of images.

            WHY THIS FUNCTION IS USEFUL:  Codebook learning erases the distinction between processing
                                          languages (the same thing as text) and processing images.  Codebook 
                                          learning is a natural fit for language processing because languages
                                          are serial structures and the most fundamental unit in such a 
            structure is a word (or a token as a subword). Once you have set the vocabulary for the 
            fundamental units, it automatically follows that any sentence would be expressible as a sequence of
            the tokens and, consequently, as a sequence of the embedding vectors for the tokens.
            
            Codebook learning as made possible by VQGAN allows an automaton to understand images in exactly 
            the same manner as described above.  What a token vocabulary is for the case of languages
            is the codebook learned by VQGAN for the case of images. The size of the codebook for VQGAN is set 
            by the user, as is the size of the token vocabulary for the case of languages. Subsequently, 
            each embedding vector at the output of the VQGAN Encode is replaced by the closest codebook vector.

            To be more specific, let's say that the user-specified size for the VQGAN codebook is 512 and the
            output of the VQGAN Encoder is of shape NxNXC where both the height and the width are equal to N 
            C is the number of channels. Such an encoder can be construed as representing an input image with 
            N^2 embedding vectors, each of size C.  Subsequently, the Vector Quantizer will replace each of 
            these N^2 embedding vectors with the closest codebook vector and, thus, you will have a codebook 
            based representation of the input image.
             
            As you are playing with these notions with the help of this function, you become curious as to 
            what exactly in the images is represented by the codebook vectors, Could the different codebook 
            vectors represent, say, the different types of textures in an image. As you will discover by 
            playing with this function, at this moment in time, there are no good answers to this question. 
            To illustrate, suppose the codebook is learned through just a small number of epochs and that 
            the final value for the perplexity is, say, just around 2.0, that means your codebook will 
            contain only a couple of significant vectors (despite the fact that the codebook size you 
            trained with was, say, 512). In such a case, when you map the N^2 embedding vectors at the 
            output of the VQGAN Encoder to the integer indices associated with the closest codebook vectors, 
            you are likely to see just a couple of different integer indices in the N^2-element long list.  
            What's interesting is that even with just two different integer indices, the outputs produced by 
            the VQGAN Decoder would look very different depending on the positions occupied by the two 
            different codebook vectors.  For example, for the case when the VQGAN encode produces an 8x8 
            array at its output (when means that an input image would be represented by 64 embeddings),
            the following sequence of integer indices

                219,219,219,219,15,15,15,15,219,15,15,219,15,15,15,15,15,15,219,219,15,15,15,15,15,15,15, 
                219,219,15,15,15,15,15,15,219,219,15,15,15,15,15,15,15,219,15,15,15,15,15,15,15,15,15,15,  
                15,15,15,15,15,15,15,15,15
 
            may lead the VQGAN Decoder to output a sunflower image and the following sequence, on the other
            hand,

                15,15,15,15,15,15,15,15,15,15,15,15,15,219,15,15,15,15,15,15,219,219,15,15,15,15,15,219,15, 
                219,15,15,15,15,219,219,15,219,15,15,15,15,15,219,15,219,15,15,15,15,15,219,15,15,15,15,15,  
                15,15,15,15,15,15,15

            may lead to the image of a rose. I am mentioning the names of the flowers in my explanation 
            because my observations are based on my experiments with the flower dataset from the Univ of
            Oxford.
            """
            def normed_tensor(x):
                norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
                return x / (norm_factor + 1e-10)

            self.vqgan_encoder.load_state_dict(torch.load("checkpoint_dir/vqgan_encoder_99"))
            self.vqgan_decoder.load_state_dict(torch.load("checkpoint_dir/vqgan_decoder_99"))
            self.vqgan_vector_quantizer.load_state_dict(torch.load("checkpoint_dir/vqgan_vector_quantizer_99"))
            self.vqgan_pre_vq_convo.load_state_dict(torch.load("checkpoint_dir/vqgan_pre_vq_convo_99"))
            self.vqgan_post_vq_convo.load_state_dict(torch.load("checkpoint_dir/vqgan_post_vq_convo_99"))
            self.codebook = super(DLStudio.VQGAN, self).VectorQuantizerEMA.static_codebook
            self.codebook.load_state_dict(torch.load("checkpoint_dir/codebook_99"))
            if im_name:
                im_as_array =  Image.open( im_name )
                transform = tvt.Compose( [tvt.Resize((64,64)), 
                                          tvt.CenterCrop((64,64)),         
                                          tvt.ToTensor(), 
                                          tvt.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))] )
                im_as_tensor = transform( im_as_array )
                ##  Add batch axis:
                im_as_tensor  =  torch.unsqueeze( im_as_tensor, 0 )
            else:
                ## Multithreaded dataloader does not allow for a batch to be drawn randomly. So here's
                ## using an admittedly primitive ploy to get around that:
                for _ in range(random.randint(1,20)):
                    next(iter(self.train_dataloader))
                im_as_tensor = next(iter(self.train_dataloader))
                im_as_tensor = im_as_tensor[0]
            torch.set_printoptions(edgeitems=10_000, linewidth=120)
            z = self.vqgan_encoder(normed_tensor(im_as_tensor))
            z = self.pre_vq_convo(z)
            vq_loss, quantized, perplexity, encoding_indices_as_onehot_vecs =  self.vqgan_vector_quantizer(z)
            encoding_indices_as_ints = encoding_indices_as_onehot_vecs.argmax(1) 
            if im_name:
                print("\n\nFor image %s the encoding indices are:" % im_name)
                print(encoding_indices_as_ints)
            else:
                print("\n\nFor the batch, the encoding indices are are:")           
                batch_size = im_as_tensor.shape[0]
                how_many_per_image = len( encoding_indices_as_ints ) // batch_size
                for i in range(batch_size):
                   print("\nimage %d: %s" % (i, encoding_indices_as_ints[i*how_many_per_image : (i+1)*how_many_per_image]))
            torch.set_printoptions(profile="default")
            z = self.post_vq_convo(quantized)
            decoder_out = self.vqgan_decoder(z)
            decoder_out = normed_tensor(decoder_out)
            self.display_2_images(im_as_tensor, decoder_out)


        def run_code_for_transformer_based_modeling_VQGAN(self, vqgan, epochs_for_xformer_training, max_seq_length, embedding_size, codebook_size,
                     num_warmup_steps, optimizer_params, num_basic_decoders, num_atten_heads, masking, checkpoint_dir, visualization_dir ):
            """ 
            After codebook learning, for what I am going to focus on now, note that VQGAN Generator returns a sequence 
            of integers that are the indices of the codebook vectors for each of the embedding vectors at the output
            of the Encoder. To elaborate, assume that the Encoder outputs an NxNxC array where C is the number of 
            channels.  We can think of each of the N^2 array elements at the Encoder output as the embedding vectors, 
            with the embedding dimension being equal to C.

            Let's say S is the size of the codebook. The Vector Quantizer's job in VQGAN is to return the closest 
            codebook vector for each of the N^2 embedding vectors mentioned above.  If you look at what is returned
            by the class
                                       VectorQuantizerEMA            

            in VQGAN's parent class VQVAE, you will see the following as the last statement for the above:

                    return loss, quantized.permute(0, 3, 1, 2).contiguous(), perplexity, encodings

            where "quantized" is a sequence of codebook vectors that are the closest approximations to the N^2 
            embedding vectors at the output of the Encoder and where "encodings" is a sequence of integer index
            values associated with the codebook vectors in "quantized".

            The focus now is on the integer sequence in "encodings".

            The integer sequence that you see in "encodings" is no different from the integer sequence you would
            use for the tokens in a sentence in natural language processing (NLP).  For NLP, the tokenizer that
            you train for a given corpus gives you a token vocabulary that has a prescribed size of, say, 30,000.
            Based on the relative frequencies of the words from which the tokens are derived, the tokenizer 
            gives you a set of tokens, the total number of which will be bounded by the prescribed size, and, for
            each token its integer mapping.  Subsequently, for all neural-network based downstream processing, 
            you will represent text through a token sequence that, in effect, will be a sequence of integer index
            values.

            You can therefore say that what a VQGAN gives you through "encodings" obliterates the difference between
            image processing and language processing and you can think of the Vector Quantizer (VQ) as the tokenizer
            in NLP. After the VQ has learned the codebook, those are your tokens --- in their embedding vector 
            representations.  

            The above implies that just as you can do autoregressive modeling of text, you should be able to carry
            our autoregressive modeling of images through the tokens, meaning through the codebook vectors.
            The goal of the implementation shown below is to illustrate exactly that.

            """
            if os.path.exists(checkpoint_dir):                    ### this checkpoint_dir is just for transformer training
                files = glob.glob(checkpoint_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(checkpoint_dir)   

            if os.path.exists(visualization_dir):                 ### this visualization_dir is just for transformer training
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   

            def normed_tensor(x):
                norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
                return x / (norm_factor + 1e-10)

            self.vqgan_encoder.load_state_dict(torch.load("checkpoint_dir/vqgan_encoder_99"))
            self.vqgan_decoder.load_state_dict(torch.load("checkpoint_dir/vqgan_decoder_99"))
            self.vqgan_vector_quantizer.load_state_dict(torch.load("checkpoint_dir/vqgan_vector_quantizer_99"))
            self.vqgan_pre_vq_convo.load_state_dict(torch.load("checkpoint_dir/vqgan_pre_vq_convo_99"))
            self.vqgan_post_vq_convo.load_state_dict(torch.load("checkpoint_dir/vqgan_post_vq_convo_99"))
            self.codebook = super(DLStudio.VQGAN, self).VectorQuantizerEMA.static_codebook
            self.codebook.load_state_dict(torch.load("checkpoint_dir/codebook_99"))

            self.vqgan_encoder.to(self.dl_studio.device)
            self.vqgan_decoder.to(self.dl_studio.device)
            self.vqgan_vector_quantizer.to(self.dl_studio.device)
            self.vqgan_pre_vq_convo.to(self.dl_studio.device)
            self.vqgan_post_vq_convo.to(self.dl_studio.device)
            self.codebook.to(self.dl_studio.device)

            vocab_size = codebook_size
            xformer = DLStudio.TransformerFG( max_seq_length, embedding_size, vocab_size, num_warmup_steps, optimizer_params).to(self.dl_studio.device)
            master_decoder = DLStudio.MasterDecoderWithMasking(xformer, num_basic_decoders, num_atten_heads, masking).to(self.dl_studio.device)
            print("\nNumber of learnable params in Master Decoder: ", sum(p.numel() for p in master_decoder.parameters() if p.requires_grad))
            beta1,beta2,epsilon = optimizer_params['beta1'], optimizer_params['beta2'], optimizer_params['epsilon']     
            master_decoder_optimizer = DLStudio.ScheduledOptim(optim.Adam(master_decoder.parameters(), betas=(beta1,beta2), eps=epsilon),
                                                lr_mul=2, d_model=embedding_size, n_warmup_steps=num_warmup_steps)    
            max_seq_length = max_seq_length   ##  was set to  "encoder_out_size[0] * encoder_out_size[1]  + 2"  with 2 for SoS and EoS tokens
            criterion = nn.NLLLoss()                                                                                            
            accum_times = []
            start_time = time.perf_counter()
            batch_size = self.dl_studio.batch_size
            print("\nbatch_size: ", batch_size)
            num_batches_in_data_source = len(self.train_dataloader)
            total_num_updates = self.dl_studio.epochs * num_batches_in_data_source
            print("\nnumber of batches in the dataset: ", num_batches_in_data_source)
            training_loss_tally = []
            running_loss = 0.0
            ##  Initialize the SoS and EoS tokens, make them batch wide. Subsequently, during
            ##   training, you will attach SoS at the beginning of the integer indices sequence
            ##   for the codebook vector. And you will attach the EOS at the end.
            SoS_token = nn.Parameter( torch.randn(1,embedding_size, 1)).cuda()
            SoS_token_label = max_seq_length
            EoS_token = nn.Parameter( torch.randn(1,embedding_size, 1)).cuda()
            EoS_token_label = max_seq_length + 1
            debug = False
            print("\n\n\n           BE PATIENT! Transformers are slow to train --- especially on typical university lab hardware\n")
            for epoch in range(epochs_for_xformer_training):                                                              
                print("")
                print("\nepoch index: ", epoch)
                running_xformer_loss =  0.0
                ##  I am using a dataloader that expects a list of images in a batch followed by 
                ##  a list of the corresponding target label integers.  In our case, though, we only
                ##  have the images.  I synthesize the target label integers separately in what follows.
                for training_iter, data in enumerate(self.train_dataloader):                                    
                    master_decoder_optimizer.zero_grad()
                    input_images, _ = data                              
                    input_images = input_images.cuda()
                    input_images = normed_tensor(input_images)
                    batch_size = input_images.shape[0]                   ##  This may change at the end of an epoch
                    ##  Preparing the end tokens, SoS and EoS, for feeding into the transformer:
                    SoS_token_batch = SoS_token.repeat(batch_size,1,1)   ##  Repeat for each batch instance
                    SoS_token_batch = torch.transpose(SoS_token_batch, 1,2)
                    EoS_token_batch = EoS_token.repeat(batch_size,1,1)   ##  Repeat for each batch instance
                    EoS_token_batch = torch.transpose(EoS_token_batch, 1,2)
                    ##  Feeding the input image batch into the VQGAN Encoder:
                    z = self.vqgan_encoder(normed_tensor(input_images)).cuda()
                    z = self.pre_vq_convo(z)
                    ##  The Vector Quantizer will give us both the integer indices (as onehot vecs) and
                    ##  the codebook vectors associated with the input batch:
                    vq_loss, quantized, perplexity, encoding_indices_as_onehot_vecs =  self.vqgan_vector_quantizer(z)
                    ##  We need to turn the onehot vecs for the integer indices into actual integer values:
                    encoding_indices_as_ints = encoding_indices_as_onehot_vecs.argmax(1) 
                    ##  Now we must prepare the ground-truth target labels for the transformer:
                    indices_tensor = torch.tensor(encoding_indices_as_ints)
                    indices_tensor = indices_tensor.view(z.shape[0], -1).cuda()
                    target_labels = torch.zeros(size=(batch_size, max_seq_length), dtype=torch.int64).cuda()
                    target_labels[:,1:-1] = indices_tensor
                    target_labels[:,0] = SoS_token_label
                    target_labels[:,-1] = EoS_token_label
                    ##  Let's now process the codebook vectors that correspond to the above integer indices since
                    ##  they are going to be used as the embedding vectors associated with the above integer indices:
                    quantized =  quantized.reshape(z.shape[0], z.shape[1], -1).cuda()
                    ##  We need to now synthesize the input tensor for the transformer: 
                    input_tensor = torch.transpose(quantized, 1,2).cuda()   
                    input_tensor = torch.cat( (SoS_token_batch, input_tensor, EoS_token_batch), dim=1 )
                    predicted_indices = torch.zeros(batch_size, max_seq_length, dtype=torch.int64).cuda()
                    mask = torch.ones(1, dtype=int)                         ## initialize the mask                      
                    LOSS = 0.0
                    for word_index in range(1,input_tensor.shape[1]):
                        masked_input_seq = master_decoder.apply_mask(input_tensor, mask)                                
                        predicted_word_logprobs, predicted_word_index_values = master_decoder(input_tensor, mask)
                        predicted_indices[:,word_index] = predicted_word_index_values
                        loss = criterion(predicted_word_logprobs, target_labels[:, word_index])           
                        LOSS += loss
                        mask = torch.cat( ( mask, torch.ones(1, dtype=int) ) )                                          
                    predicted_indices = np.array(predicted_indices.cpu())
                    LOSS.backward()
                    master_decoder_optimizer.step_and_update_lr()                                                       
                    loss_normed = LOSS.item() / input_tensor.shape[0]
                    running_loss += loss_normed
                    prev_seq_logprobs  =  predicted_word_logprobs
                    if training_iter % 100 == 99:    
                        avg_loss = running_loss / float(100)
                        training_loss_tally.append(avg_loss)
                        running_loss = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%2d/%d  iter:%4d  elapsed_time: %4d secs]     loss: %.4f" % (epoch+1,self.dl_studio.epochs,training_iter+1,time_elapsed,avg_loss)) 
                        accum_times.append(current_time-start_time)
                ##  At the beginning of the training session, the designated checkpoint_dir has already been flushed
                torch.save(master_decoder.state_dict(), checkpoint_dir + "/master_decoder_" +  str(epoch))
            print("\nFinished Training\n")
            plt.figure(figsize=(10,5))
            plt.title("FG Training Loss vs. Iterations")
            plt.plot(training_loss_tally)
            plt.xlabel("iterations")
            plt.ylabel("training loss")
            plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
            plt.savefig("training_loss_FG_" +  str(self.dl_studio.epochs) + ".png")
            plt.show()



        def run_code_for_evaluating_transformer_based_modeling_using_VQGAN(self, vqgan, max_seq_length, embedding_size, codebook_size, 
                num_basic_decoders, num_atten_heads, masking, xformer_checkpoint, visualization_dir = "vqgan_xformer_visualization_dir" ):
            """
            After the VQGAN transformer has been trained as described in the prevous "run_code_" method, we need
            to test the transformer model on previously unseen images.
            """
            if os.path.exists(visualization_dir):  
                """
                Clear out the previous outputs in the visualization directory
                """
                files = glob.glob(visualization_dir + "/*")
                for file in files: 
                    if os.path.isfile(file): 
                        os.remove(file) 
                    else: 
                        files = glob.glob(file + "/*") 
                        list(map(lambda x: os.remove(x), files)) 
            else: 
                os.mkdir(visualization_dir)   

            def normed_tensor(x):
                norm_factor = torch.sqrt(torch.sum(x**2, dim=1, keepdim=True))
                return x / (norm_factor + 1e-10)

            self.vqgan_encoder.load_state_dict(torch.load("checkpoint_dir/vqgan_encoder_99"))
            self.vqgan_decoder.load_state_dict(torch.load("checkpoint_dir/vqgan_decoder_99"))
            self.vqgan_vector_quantizer.load_state_dict(torch.load("checkpoint_dir/vqgan_vector_quantizer_99"))
            self.vqgan_pre_vq_convo.load_state_dict(torch.load("checkpoint_dir/vqgan_pre_vq_convo_99"))
            self.vqgan_post_vq_convo.load_state_dict(torch.load("checkpoint_dir/vqgan_post_vq_convo_99"))
            self.codebook = super(DLStudio.VQGAN, self).VectorQuantizerEMA.static_codebook
            self.codebook.load_state_dict(torch.load("checkpoint_dir/codebook_99"))

            self.vqgan_encoder.cuda()
            self.vqgan_decoder.cuda()
            self.vqgan_vector_quantizer.cuda()
            self.vqgan_pre_vq_convo.cuda()
            self.vqgan_post_vq_convo.cuda()
            self.codebook.cuda()

            vocab_size = codebook_size
            xformer = DLStudio.TransformerFG( max_seq_length, embedding_size, vocab_size)
            master_decoder = DLStudio.MasterDecoderWithMasking(xformer, num_basic_decoders, num_atten_heads, masking).cuda()
            master_decoder.load_state_dict(torch.load(xformer_checkpoint))
            master_decoder.cuda()

            SoS_token = nn.Parameter( torch.randn(1,embedding_size, 1)).cuda()
            SoS_token_label = max_seq_length
            EoS_token = nn.Parameter( torch.randn(1,embedding_size, 1)).cuda()
            EoS_token_label = max_seq_length + 1

            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):                                    
                    print("\n\n\n=========Showing VQGAN Tranformer results for test batch %d===============" % i)
                    torch.set_printoptions(edgeitems=10_000, linewidth=120)
                    test_images, _ = data     
                    test_images = test_images.cuda()
                    batch_size = test_images.shape[0]             
                    z = self.vqgan_encoder(normed_tensor(test_images)).cuda()
                    input_shape = z.shape                               ## to be used later on the output of the transformer
                    z = self.pre_vq_convo(z)
                    _, quantized, _, encoding_indices_as_onehot_vecs =  self.vqgan_vector_quantizer(z)
                    encoding_indices_as_ints = encoding_indices_as_onehot_vecs.argmax(1) 
                    indices_tensor = torch.tensor(encoding_indices_as_ints)
                    indices_tensor = indices_tensor.view(z.shape[0], -1).cuda()
                    quantized =  quantized.reshape(z.shape[0], z.shape[1], -1).cuda()
                    test_images_tensor = torch.transpose(quantized, 1,2).cuda()
                    SoS_token_batch = SoS_token.repeat(batch_size,1,1)   ##  Repeat for each batch instance
                    SoS_token_batch = torch.transpose(SoS_token_batch, 1,2)
                    EoS_token_batch = EoS_token.repeat(batch_size,1,1)   ##  Repeat for each batch instance
                    EoS_token_batch = torch.transpose(EoS_token_batch, 1,2)
                    test_images_tensor = torch.cat( (SoS_token_batch, test_images_tensor, EoS_token_batch), dim=1 )
                    mask = torch.ones(1, dtype=int)                         ## initialize the mask                      
                    predicted_indices = torch.zeros(batch_size, max_seq_length, dtype=torch.int64).cuda()
                    for word_index in range(1,test_images_tensor.shape[1]):
                        masked_input_seq = master_decoder.apply_mask(test_images_tensor, mask)                                
                        predicted_word_logprobs, predicted_word_index_values = master_decoder(test_images_tensor, mask)
                        predicted_indices[:,word_index] = predicted_word_index_values
#                    print("\n\nPredicted indices for the images: ", predicted_indices)
                    torch.set_printoptions(profile="default")
                    ##  We now convert the integer-valued index values for the codebook vectors into onehot vector
                    ##  representations of the same.  Subsequently, we matix-multiply the tensor of one-hot vectors
                    ##  with the "matrix" that represents the codebook vector weights to get the sequence of the codebook
                    ##  vectors for the output of the transformer. Thiese can then be fed into the VQGAN Decoder to 
                    ##  to construct the output image:
                    onehot_encodings = torch.zeros(batch_size * (max_seq_length-2), codebook_size).cuda()  ## max_seq_length inludes 
                                                                                                           ##  the two end tokens
                    onehot_encodings.scatter_(1, predicted_indices[1:-1], 1)    
                    quantized = torch.matmul(onehot_encodings, self.codebook.weight)
                    quantized = quantized.view(input_shape)
                    z = self.post_vq_convo(quantized)
                    decoder_out = self.vqgan_decoder(z)
                    decoder_out = normed_tensor(decoder_out)
#                    self.display_2_images(test_images, decoder_out)
                    together = torch.zeros( test_images.shape[0], test_images.shape[1], test_images.shape[2], 2 * test_images.shape[3], dtype=torch.float )
                    together[:,:,:,0:test_images.shape[3]]  =  test_images
                    together[:,:,:,test_images.shape[3]:]  =   decoder_out 
                    plt.figure(figsize=(40,20))
                    plt.imshow(np.transpose(torchvision.utils.make_grid(together.cpu(), normalize=False, padding=3, pad_value=255).cpu(), (1,2,0)))
                    plt.title("VQGAN Output Images for iteration %d" % i)
                    plt.savefig(visualization_dir + "/vqgan_transformer_decoder_out_%s" % str(i) + ".png")
                    plt.show()


    ########################################  Start Definition of Inner Class TransformerFG  ####################################

    class TransformerFG(nn.Module):             
        """
        I have borrowed from the DLStudio's Transformers module.  "FG" stands for "First Generation" --- which is the Transformer
        as originally proposed by Vaswani et al.
        """
        def __init__(self, max_seq_length, embedding_size, vocab_size, num_warmup_steps=None, optimizer_params=None):
            super(DLStudio.TransformerFG, self).__init__()
            self.max_seq_length = max_seq_length
            self.embedding_size = embedding_size
            self.num_warmup_steps = num_warmup_steps
            self.optimizer_params = optimizer_params
            self.vocab_size = vocab_size
    
    class EmbeddingGenerator(nn.Module):
        def __init__(self, xformer, embedding_size):
            super(DLStudio.EmbeddingGenerator, self).__init__()
            self.vocab_size =  xformer.vocab_size
            self.embedding_size = embedding_size                                             
            self.max_seq_length = xformer.max_seq_length                                                     
            self.embed = nn.Embedding(self.vocab_size, embedding_size)

        def forward(self, sentence_tensor):                                                                 
            sentence_tensor = sentence_tensor
            ## Let's say your batch_size is 4 and that each sentence has a max_seq_length of 10.
            ## The sentence_tensor argument will now be of shape [4,10].  If the embedding size is
            ## is 512, the following call will return a tensor of shape [4,10,512)
            word_embeddings = self.embed(sentence_tensor)
            position_coded_word_embeddings = self.apply_positional_encoding( word_embeddings )
            return position_coded_word_embeddings

        def apply_positional_encoding(self, sentence_tensor):
            position_encodings = torch.zeros_like( sentence_tensor ).float()
            ## Calling unsqueeze() with arg 1 causes the "row tensor" to turn into a "column tensor"
            ##    which is needed in the products shown below. We create a 2D pattern by 
            ##    taking advantage of how PyTorch has overloaded the definition of the infix '*' 
            ##    tensor-tensor multiplication operator.  It in effect creates an output-product of
            ##    of what is essentially a column vector with what is essentially a row vector.
            word_positions = torch.arange(0, self.max_seq_length).unsqueeze(1)            
            div_term =  1.0 / (100.0 ** ( 2.0 * torch.arange(0, self.embedding_size, 2) / float(self.embedding_size) ))
            position_encodings[:, :, 0::2] =  torch.sin(word_positions * div_term)                             
            position_encodings[:, :, 1::2] =  torch.cos(word_positions * div_term)                             
            return sentence_tensor + position_encodings


    ###################################  Self Attention Code for TransformerFG  ###########################################

    class SelfAttention(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_atten_heads):
            super(DLStudio.SelfAttention, self).__init__()
            self.max_seq_length = xformer.max_seq_length                                                     
            self.embedding_size = xformer.embedding_size
            self.num_atten_heads = num_atten_heads
            self.qkv_size = self.embedding_size // num_atten_heads
            self.attention_heads_arr = nn.ModuleList( [DLStudio.AttentionHead(self.max_seq_length, 
                                    self.qkv_size, num_atten_heads)  for _ in range(num_atten_heads)] )           

        def forward(self, sentence_tensor):                                                                       
            concat_out_from_atten_heads = torch.zeros( sentence_tensor.shape[0], self.max_seq_length, 
                                                                  self.num_atten_heads * self.qkv_size).float()
            for i in range(self.num_atten_heads):                                                                 
                sentence_embed_slice = sentence_tensor[:, :, i * self.qkv_size : (i+1) * self.qkv_size]
                concat_out_from_atten_heads[:, :, i * self.qkv_size : (i+1) * self.qkv_size] =          \
                                                               self.attention_heads_arr[i](sentence_embed_slice)   
            return concat_out_from_atten_heads


    class AttentionHead(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self,  max_seq_length, qkv_size, num_atten_heads):
            super(DLStudio.AttentionHead, self).__init__()
            self.qkv_size = qkv_size
            self.max_seq_length = max_seq_length
            self.WQ =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.WK =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.WV =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.softmax = nn.Softmax(dim=-1)                                                                          

        def forward(self, sent_embed_slice):           ## sent_embed_slice == sentence_embedding_slice                
            Q = self.WQ( sent_embed_slice )                                                                           
            K = self.WK( sent_embed_slice )                                                                           
            V = self.WV( sent_embed_slice )                                                                           
            A = K.transpose(2,1)                                                                                      
            QK_dot_prod = Q @ A                                                                                       
            rowwise_softmax_normalizations = self.softmax( QK_dot_prod )                                              
            Z = rowwise_softmax_normalizations @ V                                                                    
            coeff = 1.0/torch.sqrt(torch.tensor([self.qkv_size]).float()).cuda()
            Z = coeff * Z                                                                          
            return Z


    #########################################  Basic Decoder Class for TransformerFG  #####################################

    class BasicDecoderWithMasking(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_atten_heads, masking=True):
            super(DLStudio.BasicDecoderWithMasking, self).__init__()
            self.masking = masking
            self.embedding_size = xformer.embedding_size                                             
            self.max_seq_length = xformer.max_seq_length                                                     
            self.num_atten_heads = num_atten_heads
            self.qkv_size = self.embedding_size // num_atten_heads
            self.self_attention_layer = DLStudio.SelfAttention(xformer, num_atten_heads)
            self.norm1 = nn.LayerNorm(self.embedding_size)
            self.norm2 = nn.LayerNorm(self.embedding_size)
            ## What follows are the linear layers for the FFN (Feed Forward Network) part of a BasicDecoder
            self.W1 =  nn.Linear( self.embedding_size, 4 * self.embedding_size )
            self.W2 =  nn.Linear( 4 * self.embedding_size, self.embedding_size ) 
            self.norm3 = nn.LayerNorm(self.embedding_size)

        def forward(self, sentence_tensor, mask):   
            masked_sentence_tensor = self.apply_mask(sentence_tensor, mask)
            Z_concatenated = self.self_attention_layer(masked_sentence_tensor).cuda()
            Z_out = self.norm1(Z_concatenated + masked_sentence_tensor)                     
            ## for FFN:
            basic_decoder_out =  nn.ReLU()(self.W1( Z_out.view( sentence_tensor.shape[0], self.max_seq_length, -1) ))                  
            basic_decoder_out =  self.W2( basic_decoder_out )                                                    
            basic_decoder_out = basic_decoder_out.view(sentence_tensor.shape[0], self.max_seq_length, self.embedding_size )
            basic_decoder_out =  basic_decoder_out  + Z_out 
            basic_decoder_out = self.norm3( basic_decoder_out )
            return basic_decoder_out

        def apply_mask(self, sentence_tensor, mask):  
            out = torch.zeros_like(sentence_tensor).float().cuda()
            out[:,:len(mask),:] = sentence_tensor[:,:len(mask),:] 
            return out    


    ######################################  MasterDecoder Class for TransformerFG #########################################

    class MasterDecoderWithMasking(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_basic_decoders, num_atten_heads, masking=True):
            super(DLStudio.MasterDecoderWithMasking, self).__init__()
            self.masking = masking
            self.max_seq_length = xformer.max_seq_length
            self.embedding_size = xformer.embedding_size
            self.vocab_size = xformer.vocab_size                                             
            self.basic_decoder_arr = nn.ModuleList([DLStudio.BasicDecoderWithMasking( xformer,
                                                    num_atten_heads, masking) for _ in range(num_basic_decoders)])  
            ##  Need the following layer because we want the prediction of each target word to be a probability 
            ##  distribution over the target vocabulary. The conversion to probs would be done by the criterion 
            ##  nn.CrossEntropyLoss in the training loop:
            self.out = nn.Linear(self.embedding_size, self.vocab_size)                                          

        def forward(self, sentence_tensor, mask):                                                   
            out_tensor = sentence_tensor
            for i in range(len(self.basic_decoder_arr)):                                                 
                out_tensor = self.basic_decoder_arr[i](out_tensor, mask)                              
            word_index = mask.shape[0]
            last_word_tensor = out_tensor[:,word_index]                                      
            last_word_onehot = self.out(last_word_tensor)        
            output_word_logprobs = nn.LogSoftmax(dim=1)(last_word_onehot)                                     
            _, idx_max = torch.max(output_word_logprobs, 1)                
            ## the logprobs are over the entire vocabulary of the tokenizer
            return output_word_logprobs, idx_max


        def apply_mask(self, sentence_tensor, mask):  
            out = torch.zeros_like(sentence_tensor).float().cuda()
            out[:,:len(mask),:] = sentence_tensor[:,:len(mask),:] 
            return out    


    ###########################  ScheduledOptim Code for TransformerFG #############################

    class ScheduledOptim():
        """
        As in the Transformers module of DLStudio, for the scheduling of the learning rate
        during the warm-up phase of training TransformerFG, I have borrowed the class shown below
        from the GitHub code made available by Yu-Hsiang Huang at:

                https://github.com/jadore801120/attention-is-all-you-need-pytorch
        """
        def __init__(self, optimizer, lr_mul, d_model, n_warmup_steps):
            self._optimizer = optimizer
            self.lr_mul = lr_mul
            self.d_model = d_model
            self.n_warmup_steps = n_warmup_steps
            self.n_steps = 0

        def step_and_update_lr(self):
            "Step with the inner optimizer"
            self._update_learning_rate()
            self._optimizer.step()
    
        def zero_grad(self):
            "Zero out the gradients with the inner optimizer"
            self._optimizer.zero_grad()
    
        def _get_lr_scale(self):
            d_model = self.d_model
            n_steps, n_warmup_steps = self.n_steps, self.n_warmup_steps
            return (d_model ** -0.5) * min(n_steps ** (-0.5), n_steps * n_warmup_steps ** (-1.5))
    
        def _update_learning_rate(self):
            ''' Learning rate scheduling per step '''
            self.n_steps += 1
            lr = self.lr_mul * self._get_lr_scale()
            for param_group in self._optimizer.param_groups:
                param_group['lr'] = lr



    ###%%%
    #####################################################################################################################
    ####################################  Start Definition of Inner Class TextClassification  ###########################

    class TextClassification(nn.Module):             
        """
        The purpose of this inner class is to be able to use the DLStudio platform for simple 
        experiments in text classification.  Consider, for example, the problem of automatic 
        classification of variable-length user feedback: you want to create a neural network
        that can label an uploaded product review of arbitrary length as positive or negative.  
        One way to solve this problem is with a recurrent neural network in which you use a 
        hidden state for characterizing a variable-length product review with a fixed-length 
        state vector.  This inner class allows you to carry out such experiments.

        Class Path:  DLStudio -> TextClassification 
        """
        def __init__(self, dl_studio, dataserver_train=None, dataserver_test=None, dataset_file_train=None, 
                                                               dataset_file_test=None, display_train_loss=False):
            super(DLStudio.TextClassification, self).__init__()
            self.dl_studio = dl_studio
            self.dataserver_train = dataserver_train
            self.dataserver_test = dataserver_test
            self.display_train_loss = display_train_loss

        class SentimentAnalysisDataset(torch.utils.data.Dataset):
            """
            The sentiment analysis datasets that I have made available were extracted from
            an archive of user feedback comments as made available by Amazon for the year
            2007.  The original archive contains user feedback on 25 product categories. 
            For each product category, there are two files named 'positive.reviews' and
            'negative.reviews', with each file containing 1000 reviews. I believe that
            characterizing the reviews as 'positive' or 'negative' was carried out by 
            human annotators. Regardless, the reviews in these two files can be used to 
            train a neural network whose purpose would be to automatically characterize
            a product as being positive or negative. 

            I have extracted the following datasets extracted from the Amazon archive:

                 sentiment_dataset_train_200.tar.gz        vocab_size = 43,285
                 sentiment_dataset_test_200.tar.gz  

                 sentiment_dataset_train_40.tar.gz         vocab_size = 17,001
                 sentiment_dataset_test_40.tar.gz    

                 sentiment_dataset_train_3.tar.gz          vocab_size = 3,402
                 sentiment_dataset_test_3.tar.gz    

            The integer in the name of each dataset is the number of reviews collected 
            from the 'positive.reviews' and the 'negative.reviews' files for each product
            category.  Therefore, the dataset with 200 in its name has a total of 400 
            reviews for each product category.

            As to why I am presenting these three different datasets, note that, as shown
            above, the size of the vocabulary depends on the number of reviews selected
            and the size of the vocabulary has a strong bearing on how long it takes to 
            train an algorithm for text classification. For one simple reason for that: 
            the size of the one-hot representation for the words equals the size of the 
            vocabulary.  Therefore, the one-hot representation for the words for the 
            dataset with 200 in its name will be a one-axis tensor of size 43,285.

            For a purely feedforward network, it is not a big deal for the input tensors
            to be size Nx43285 where N is the number of words in a review.  And even for
            RNNs with simple feedback, that does not slow things down.  However, when 
            using GRUs, it's an entirely different matter if you are tying to run your
            experiments on, say, a laptop with a Quadro GPU.  Hence the reason for providing
            the datasets with 200 and 40 reviews.  The dataset with just 3 reviews is for
            debugging your code.

            Class Path:  DLStudio -> TextClassification -> SentimentAnalysisDataset
            """
            def __init__(self, dl_studio, train_or_test, dataset_file):
                super(DLStudio.TextClassification.SentimentAnalysisDataset, self).__init__()
                self.train_or_test = train_or_test
                root_dir = dl_studio.dataroot
                f = gzip.open(root_dir + dataset_file, 'rb')
                dataset = f.read()
                if train_or_test == 'train':
                    if sys.version_info[0] == 3:
                        self.positive_reviews_train, self.negative_reviews_train, self.vocab = pickle.loads(dataset, encoding='latin1')
                    else:
                        self.positive_reviews_train, self.negative_reviews_train, self.vocab = pickle.loads(dataset)
                    self.categories = sorted(list(self.positive_reviews_train.keys()))
                    self.category_sizes_train_pos = {category : len(self.positive_reviews_train[category]) for category in self.categories}
                    self.category_sizes_train_neg = {category : len(self.negative_reviews_train[category]) for category in self.categories}
                    self.indexed_dataset_train = []
                    for category in self.positive_reviews_train:
                        for review in self.positive_reviews_train[category]:
                            self.indexed_dataset_train.append([review, category, 1])
                    for category in self.negative_reviews_train:
                        for review in self.negative_reviews_train[category]:
                            self.indexed_dataset_train.append([review, category, 0])
                    random.shuffle(self.indexed_dataset_train)
                elif train_or_test == 'test':
                    if sys.version_info[0] == 3:
                        self.positive_reviews_test, self.negative_reviews_test, self.vocab = pickle.loads(dataset, encoding='latin1')
                    else:
                        self.positive_reviews_test, self.negative_reviews_test, self.vocab = pickle.loads(dataset)
                    self.vocab = sorted(self.vocab)
                    self.categories = sorted(list(self.positive_reviews_test.keys()))
                    self.category_sizes_test_pos = {category : len(self.positive_reviews_test[category]) for category in self.categories}
                    self.category_sizes_test_neg = {category : len(self.negative_reviews_test[category]) for category in self.categories}
                    self.indexed_dataset_test = []
                    for category in self.positive_reviews_test:
                        for review in self.positive_reviews_test[category]:
                            self.indexed_dataset_test.append([review, category, 1])
                    for category in self.negative_reviews_test:
                        for review in self.negative_reviews_test[category]:
                            self.indexed_dataset_test.append([review, category, 0])
                    random.shuffle(self.indexed_dataset_test)

            def get_vocab_size(self):
                return len(self.vocab)

            def one_hotvec_for_word(self, word):
                word_index =  self.vocab.index(word)
                hotvec = torch.zeros(1, len(self.vocab))
                hotvec[0, word_index] = 1
                return hotvec

            def review_to_tensor(self, review):
                review_tensor = torch.zeros(len(review), len(self.vocab))
                for i,word in enumerate(review):
                    review_tensor[i,:] = self.one_hotvec_for_word(word)
                return review_tensor

            def sentiment_to_tensor(self, sentiment):
                """
                Sentiment is ordinarily just a binary valued thing.  It is 0 for negative
                sentiment and 1 for positive sentiment.  We need to pack this value in a
                two-element tensor.
                """        
                sentiment_tensor = torch.zeros(2)
                if sentiment == 1:
                    sentiment_tensor[1] = 1
                elif sentiment == 0: 
                    sentiment_tensor[0] = 1
                sentiment_tensor = sentiment_tensor.type(torch.long)
                return sentiment_tensor

            def __len__(self):
                if self.train_or_test == 'train':
                    return len(self.indexed_dataset_train)
                elif self.train_or_test == 'test':
                    return len(self.indexed_dataset_test)

            def __getitem__(self, idx):
                sample = self.indexed_dataset_train[idx] if self.train_or_test == 'train' else self.indexed_dataset_test[idx]
                review = sample[0]
                review_category = sample[1]
                review_sentiment = sample[2]
                review_sentiment = self.sentiment_to_tensor(review_sentiment)
                review_tensor = self.review_to_tensor(review)
                category_index = self.categories.index(review_category)
                sample = {'review'       : review_tensor, 
                          'category'     : category_index, # should be converted to tensor, but not yet used
                          'sentiment'    : review_sentiment }
                return sample

        def load_SentimentAnalysisDataset(self, dataserver_train, dataserver_test ):   
            self.train_dataloader = torch.utils.data.DataLoader(dataserver_train,
                        batch_size=self.dl_studio.batch_size,shuffle=True, num_workers=1)
            self.test_dataloader = torch.utils.data.DataLoader(dataserver_test,
                               batch_size=self.dl_studio.batch_size,shuffle=False, num_workers=1)

        class TEXTnet(nn.Module):
            """
            This network is meant for semantic classification of variable-length sentiment 
            data.  Based on my limited testing, the performance of this network is very
            poor because it has no protection against vanishing gradients when used in an
            RNN.

            Class Path:  DLStudio -> TextClassification -> TEXTnet
            """
            def __init__(self, input_size, hidden_size, output_size):
                super(DLStudio.TextClassification.TEXTnet, self).__init__()
                self.input_size = input_size
                self.hidden_size = hidden_size
                self.output_size = output_size
                self.combined_to_hidden = nn.Linear(input_size + hidden_size, hidden_size)
                self.combined_to_middle = nn.Linear(input_size + hidden_size, 100)
                self.middle_to_out = nn.Linear(100, output_size)     
                self.logsoftmax = nn.LogSoftmax(dim=1)
                self.dropout = nn.Dropout(p=0.1)

            def forward(self, input, hidden):
                combined = torch.cat((input, hidden), 1)
                hidden = self.combined_to_hidden(combined)
                hidden = torch.tanh(hidden)                   
                out = self.combined_to_middle(combined)
                out = nn.functional.relu(out)
                out = self.dropout(out)
                out = self.middle_to_out(out)
                out = self.logsoftmax(out)
                return out,hidden         

            def init_hidden(self):
                hidden = torch.zeros(1, self.hidden_size)
                return hidden


        class TEXTnetOrder2(nn.Module):
            """
            In this variant of the TEXTnet network, the value of hidden as used at each
            time step also includes its value at the previous time step.  This fact, not
            directly apparent by the definition of the class shown below, is made possible
            by the last parameter, cell, in the header of forward().  As you can see below,
            at the end of forward(), the value of the cell goes through a linear layer
            and through a sigmoid nonlinearity. By the way, since the sigmoid saturates at 0
            and 1, it can act like a switch. Later when I use this class in the training
            function, you will see the cell values being used in such a manner that the
            hidden state at each time step is mixed with the hidden state at the previous
            time step, but only to the extent allowed by the switching action of the Sigmoid.

            Class Path:  DLStudio -> TextClassification -> TEXTnetOrder2
            """
            def __init__(self, input_size, hidden_size, output_size):
                super(DLStudio.TextClassification.TEXTnetOrder2, self).__init__()
                self.input_size = input_size
                self.hidden_size = hidden_size
                self.output_size = output_size
                self.combined_to_hidden = nn.Linear(input_size + 2*hidden_size, hidden_size)
                self.combined_to_middle = nn.Linear(input_size + 2*hidden_size, 100)
                self.middle_to_out = nn.Linear(100, output_size)     
                self.logsoftmax = nn.LogSoftmax(dim=1)
                self.dropout = nn.Dropout(p=0.1)
                # for the cell
                self.linear_for_cell = nn.Linear(hidden_size, hidden_size)

            def forward(self, input, hidden, cell):
                combined = torch.cat((input, hidden, cell), 1)
                hidden = self.combined_to_hidden(combined)
                hidden = torch.tanh(hidden)                     
                out = self.combined_to_middle(combined)
                out = nn.functional.relu(out)
                out = self.dropout(out)
                out = self.middle_to_out(out)
                out = self.logsoftmax(out)
                hidden_clone = hidden.clone()
                cell = torch.sigmoid(self.linear_for_cell(hidden_clone))
                return out,hidden,cell         

            def initialize_cell(self):
                weight = next(self.linear_for_cell.parameters()).data
                cell = weight.new(1, self.hidden_size).zero_()
                return cell

            def init_hidden(self):
                hidden = torch.zeros(1, self.hidden_size)
                return hidden


        class GRUnet(nn.Module):
            """
            Source: https://blog.floydhub.com/gru-with-pytorch/
            with the only modification that the final output of forward() is now
            routed through LogSoftmax activation. 

            In the definition shown below, input_size is the size of the vocabulary, the 
            hidden_size is typically 512, and the output_size is set to 2 for the two
            sentiments, positive and negative. 

            Class Path: DLStudio  ->  TextClassification  ->  GRUnet
            """
            def __init__(self, input_size, hidden_size, output_size, num_layers, drop_prob=0.2):
                super(DLStudio.TextClassification.GRUnet, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.gru = nn.GRU(input_size, hidden_size, num_layers)
                self.fc = nn.Linear(hidden_size, output_size)
                self.relu = nn.ReLU()
                self.logsoftmax = nn.LogSoftmax(dim=1)
                
            def forward(self, x, h):
                out, h = self.gru(x, h)
                out = self.fc(self.relu(out[:,-1]))
                out = self.logsoftmax(out)
                return out, h

            def init_hidden(self):
                weight = next(self.parameters()).data
                #                                     batch_size   
                hidden = weight.new(  self.num_layers,     1,         self.hidden_size   ).zero_()
                return hidden

        def save_model(self, model):
            "Save the trained model to a disk file"
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)


        def run_code_for_training_with_TEXTnet(self, net, display_train_loss=False):        
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net.to(self.dl_studio.device)
            ## Note that the TEXTnet and TEXTnetOrder2 both produce LogSoftmax output:
            criterion = nn.NLLLoss()
            accum_times = []
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            start_time = time.perf_counter()
            training_loss_tally = []
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    hidden = net.init_hidden().to(self.dl_studio.device)              
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    sentiment = sentiment.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    input = torch.zeros(1,review_tensor.shape[2])
                    input = input.to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden = net(input, hidden)
                    loss = criterion(output, torch.argmax(sentiment,1))
                    running_loss += loss.item()
#                    loss.backward(retain_graph=True)        
                    loss.backward()        
                    optimizer.step()
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss)
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%d  iter:%4d  elapsed_time: %4d secs]     loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                        accum_times.append(current_time-start_time)
                        FILE.write("%.3f\n" % avg_loss)
                        FILE.flush()
                        running_loss = 0.0
            print("\nFinished Training\n")
            self.save_model(net)
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
#                plt.legend()
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()


        def run_code_for_training_with_TEXTnetOrder2(self, net, display_train_loss=False):        
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net.to(self.dl_studio.device)
            ## Note that the TEXTnet and TEXTnetOrder2 both produce LogSoftmax output:
            criterion = nn.NLLLoss()
            accum_times = []
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            start_time = time.perf_counter()
            training_loss_tally = []
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    hidden = net.init_hidden().to(self.dl_studio.device)              
                    cell_prev = net.initialize_cell().to(self.dl_studio.device)
                    cell_prev_2_prev = net.initialize_cell().to(self.dl_studio.device)
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    sentiment = sentiment.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    input = torch.zeros(1,review_tensor.shape[2])
                    input = input.to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden, cell = net(input, hidden, cell_prev_2_prev)
                        if k == 0:
                            cell_prev = cell
                        else:
                            cell_prev_2_prev = cell_prev
                            cell_prev = cell
                    loss = criterion(output, torch.argmax(sentiment,1))
                    running_loss += loss.item()
                    loss.backward()        
                    optimizer.step()
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss)
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%d  iter:%4d  elapsed_time: %4d secs]     loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                        accum_times.append(current_time-start_time)
                        FILE.write("%.3f\n" % avg_loss)
                        FILE.flush()
                        running_loss = 0.0
            print("\nFinished Training\n")
            self.save_model(net)
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
#                plt.legend()
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()


        def run_code_for_training_for_text_classification_with_GRU(self, net, display_train_loss=False): 
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net.to(self.dl_studio.device)
            ##  Note that the GRUnet now produces the LogSoftmax output:
            criterion = nn.NLLLoss()
            accum_times = []
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            start_time = time.perf_counter()
            training_loss_tally = []
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    sentiment = sentiment.to(self.dl_studio.device)
                    ## The following type conversion needed for MSELoss:
                    ##sentiment = sentiment.float()
                    optimizer.zero_grad()
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        output, hidden = net(torch.unsqueeze(torch.unsqueeze(review_tensor[0,k],0),0), hidden)
                    ## If using NLLLoss, CrossEntropyLoss
                    loss = criterion(output, torch.argmax(sentiment, 1))
                    ## If using MSELoss:
                    ## loss = criterion(output, sentiment)     
                    running_loss += loss.item()
                    loss.backward()
                    optimizer.step()
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss)
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%d  iter:%4d  elapsed_time:%4d secs]     loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                        accum_times.append(current_time-start_time)
                        FILE.write("%.3f\n" % avg_loss)
                        FILE.flush()
                        running_loss = 0.0
            print("Total Training Time: {}".format(str(sum(accum_times))))
            print("\nFinished Training\n")
            self.save_model(net)
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
#                plt.legend()
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()


        def run_code_for_testing_with_TEXTnet(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            net.to(self.dl_studio.device)
            classification_accuracy = 0.0
            negative_total = 0
            positive_total = 0
            confusion_matrix = torch.zeros(2,2)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    input = torch.zeros(1,review_tensor.shape[2]).to(self.dl_studio.device)
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden = net(input, hidden)
                    predicted_idx = torch.argmax(output).item()
                    gt_idx = torch.argmax(sentiment).item()
                    if i % 100 == 99:
                        print("   [i=%4d]    predicted_label=%d       gt_label=%d" % (i+1, predicted_idx,gt_idx))
                    if predicted_idx == gt_idx:
                        classification_accuracy += 1
                    if gt_idx == 0: 
                        negative_total += 1
                    elif gt_idx == 1:
                        positive_total += 1
                    confusion_matrix[gt_idx,predicted_idx] += 1
            print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
            out_percent = np.zeros((2,2), dtype='float')
            out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
            out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
            out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
            out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
            print("\n\nNumber of positive reviews tested: %d" % positive_total)
            print("\n\nNumber of negative reviews tested: %d" % negative_total)
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                      "
            out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
            print(out_str + "\n")
            for i,label in enumerate(['true negative', 'true positive']):
                out_str = "%12s:  " % label
                for j in range(2):
                    out_str +=  "%18s" % out_percent[i,j]
                print(out_str)

        def run_code_for_testing_with_TEXTnetOrder2(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            net.to(self.dl_studio.device)
            classification_accuracy = 0.0
            negative_total = 0
            positive_total = 0
            confusion_matrix = torch.zeros(2,2)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    cell_prev = net.initialize_cell()
                    cell_prev_2_prev = net.initialize_cell()
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    input = torch.zeros(1,review_tensor.shape[2]).to(self.dl_studio.device)
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden, cell = net(input, hidden, cell_prev_2_prev)
                        if k == 0:
                            cell_prev = cell
                        else:
                            cell_prev_2_prev = cell_prev
                            cell_prev = cell
                    predicted_idx = torch.argmax(output).item()
                    gt_idx = torch.argmax(sentiment).item()
                    if i % 100 == 99:
                        print("   [i=%4d]    predicted_label=%d       gt_label=%d" % (i+1, predicted_idx,gt_idx))
                    if predicted_idx == gt_idx:
                        classification_accuracy += 1
                    if gt_idx == 0: 
                        negative_total += 1
                    elif gt_idx == 1:
                        positive_total += 1
                    confusion_matrix[gt_idx,predicted_idx] += 1
            print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
            out_percent = np.zeros((2,2), dtype='float')
            out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
            out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
            out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
            out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
            print("\n\nNumber of positive reviews tested: %d" % positive_total)
            print("\n\nNumber of negative reviews tested: %d" % negative_total)
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                      "
            out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
            print(out_str + "\n")
            for i,label in enumerate(['true negative', 'true positive']):
                out_str = "%12s:  " % label
                for j in range(2):
                    out_str +=  "%18s" % out_percent[i,j]
                print(out_str)


        def run_code_for_testing_text_classification_with_GRU(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            net.to(self.dl_studio.device)
            classification_accuracy = 0.0
            negative_total = 0
            positive_total = 0
            confusion_matrix = torch.zeros(2,2)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        output, hidden = net(torch.unsqueeze(torch.unsqueeze(review_tensor[0,k],0),0), hidden)
                    predicted_idx = torch.argmax(output).item()
                    gt_idx = torch.argmax(sentiment).item()
                    if i % 100 == 99:
                        print("   [i=%d]    predicted_label=%d       gt_label=%d\n\n" % (i+1, predicted_idx,gt_idx))
                    if predicted_idx == gt_idx:
                        classification_accuracy += 1
                    if gt_idx == 0: 
                        negative_total += 1
                    elif gt_idx == 1:
                        positive_total += 1
                    confusion_matrix[gt_idx,predicted_idx] += 1
            print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
            out_percent = np.zeros((2,2), dtype='float')
            out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
            out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
            out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
            out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
            print("\n\nNumber of positive reviews tested: %d" % positive_total)
            print("\n\nNumber of negative reviews tested: %d" % negative_total)
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                      "
            out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
            print(out_str + "\n")
            for i,label in enumerate(['true negative', 'true positive']):
                out_str = "%12s:  " % label
                for j in range(2):
                    out_str +=  "%18s" % out_percent[i,j]
                print(out_str)


    ###%%%
    #####################################################################################################################
    ##########################  Start Definition of Inner Class TextClassificationWithEmbeddings  #######################

    class TextClassificationWithEmbeddings(nn.Module):             
        """
        The text processing class described previously, TextClassification, was based on
        using one-hot vectors for representing the words.  The main challenge we faced
        with one-hot vectors was that the larger the size of the training dataset, the
        larger the size of the vocabulary, and, therefore, the larger the size of the
        one-hot vectors.  The increase in the size of the one-hot vectors led to a
        model with a significantly larger number of learnable parameters --- and, that,
        in turn, created a need for a still larger training dataset.  Sounds like a classic
        example of a vicious circle.  In this section, I use the idea of word embeddings
        to break out of this vicious circle.

        Word embeddings are fixed-sized numerical representations for words that are
        learned on the basis of the similarity of word contexts.  The original and still
        the most famous of these representations are known as the word2vec
        embeddings. The embeddings that I use in this section consist of pre-trained
        300-element word vectors for 3 million words and phrases as learned from Google
        News reports.  I access these embeddings through the popular Gensim library.
 
        Class Path:  DLStudio -> TextClassificationWithEmbeddings
        """
        def __init__(self, dl_studio,dataserver_train=None,dataserver_test=None,dataset_file_train=None,dataset_file_test=None):
            super(DLStudio.TextClassificationWithEmbeddings, self).__init__()
            self.dl_studio = dl_studio
            self.dataserver_train = dataserver_train
            self.dataserver_test = dataserver_test

        class SentimentAnalysisDataset(torch.utils.data.Dataset):
            """
            In relation to the SentimentAnalysisDataset defined for the TextClassification section of 
            DLStudio, the __getitem__() method of the dataloader must now fetch the embeddings from
            the word2vec word vectors.

            Class Path:  DLStudio -> TextClassificationWithEmbeddings -> SentimentAnalysisDataset
            """
            def __init__(self, dl_studio, train_or_test, dataset_file, path_to_saved_embeddings=None):
                super(DLStudio.TextClassificationWithEmbeddings.SentimentAnalysisDataset, self).__init__()
                import gensim.downloader as gen_api
#                self.word_vectors = gen_api.load("word2vec-google-news-300")
                self.path_to_saved_embeddings = path_to_saved_embeddings
                self.train_or_test = train_or_test
                root_dir = dl_studio.dataroot
                f = gzip.open(root_dir + dataset_file, 'rb')
                dataset = f.read()
                if path_to_saved_embeddings is not None:
                    import gensim.downloader as genapi
                    from gensim.models import KeyedVectors 
                    if os.path.exists(path_to_saved_embeddings + 'vectors.kv'):
                        self.word_vectors = KeyedVectors.load(path_to_saved_embeddings + 'vectors.kv')
                    else:
                        print("""\n\nSince this is your first time to install the word2vec embeddings, it may take"""
                              """\na couple of minutes. The embeddings occupy around 3.6GB of your disk space.\n\n""")
                        self.word_vectors = genapi.load("word2vec-google-news-300")               
                        ##  'kv' stands for  "KeyedVectors", a special datatype used by gensim because it 
                        ##  has a smaller footprint than dict
                        self.word_vectors.save(path_to_saved_embeddings + 'vectors.kv')    
                if train_or_test == 'train':
                    if sys.version_info[0] == 3:
                        self.positive_reviews_train, self.negative_reviews_train, self.vocab = pickle.loads(dataset, encoding='latin1')
                    else:
                        self.positive_reviews_train, self.negative_reviews_train, self.vocab = pickle.loads(dataset)
                    self.categories = sorted(list(self.positive_reviews_train.keys()))
                    self.category_sizes_train_pos = {category : len(self.positive_reviews_train[category]) for category in self.categories}
                    self.category_sizes_train_neg = {category : len(self.negative_reviews_train[category]) for category in self.categories}
                    self.indexed_dataset_train = []
                    for category in self.positive_reviews_train:
                        for review in self.positive_reviews_train[category]:
                            self.indexed_dataset_train.append([review, category, 1])
                    for category in self.negative_reviews_train:
                        for review in self.negative_reviews_train[category]:
                            self.indexed_dataset_train.append([review, category, 0])
                    random.shuffle(self.indexed_dataset_train)
                elif train_or_test == 'test':
                    if sys.version_info[0] == 3:
                        self.positive_reviews_test, self.negative_reviews_test, self.vocab = pickle.loads(dataset, encoding='latin1')
                    else:
                        self.positive_reviews_test, self.negative_reviews_test, self.vocab = pickle.loads(dataset)
                    self.vocab = sorted(self.vocab)
                    self.categories = sorted(list(self.positive_reviews_test.keys()))
                    self.category_sizes_test_pos = {category : len(self.positive_reviews_test[category]) for category in self.categories}
                    self.category_sizes_test_neg = {category : len(self.negative_reviews_test[category]) for category in self.categories}
                    self.indexed_dataset_test = []
                    for category in self.positive_reviews_test:
                        for review in self.positive_reviews_test[category]:
                            self.indexed_dataset_test.append([review, category, 1])
                    for category in self.negative_reviews_test:
                        for review in self.negative_reviews_test[category]:
                            self.indexed_dataset_test.append([review, category, 0])
                    random.shuffle(self.indexed_dataset_test)

            def review_to_tensor(self, review):
                list_of_embeddings = []
                for i,word in enumerate(review):
                    if word in self.word_vectors.key_to_index:
                        embedding = self.word_vectors[word]
                        list_of_embeddings.append(np.array(embedding))
                    else:
                        next
#                review_tensor = torch.FloatTensor( list_of_embeddings )
                review_tensor = torch.FloatTensor( np.array(list_of_embeddings) )
                return review_tensor

            def sentiment_to_tensor(self, sentiment):
                """
                Sentiment is ordinarily just a binary valued thing.  It is 0 for negative
                sentiment and 1 for positive sentiment.  We need to pack this value in a
                two-element tensor.
                """        
                sentiment_tensor = torch.zeros(2)
                if sentiment == 1:
                    sentiment_tensor[1] = 1
                elif sentiment == 0: 
                    sentiment_tensor[0] = 1
                sentiment_tensor = sentiment_tensor.type(torch.long)
                return sentiment_tensor

            def __len__(self):
                if self.train_or_test == 'train':
                    return len(self.indexed_dataset_train)
                elif self.train_or_test == 'test':
                    return len(self.indexed_dataset_test)

            def __getitem__(self, idx):
                sample = self.indexed_dataset_train[idx] if self.train_or_test == 'train' else self.indexed_dataset_test[idx]
                review = sample[0]
                review_category = sample[1]
                review_sentiment = sample[2]
                review_sentiment = self.sentiment_to_tensor(review_sentiment)
                review_tensor = self.review_to_tensor(review)
                category_index = self.categories.index(review_category)
                sample = {'review'       : review_tensor, 
                          'category'     : category_index, # should be converted to tensor, but not yet used
                          'sentiment'    : review_sentiment }
                return sample

        def load_SentimentAnalysisDataset(self, dataserver_train, dataserver_test ):   
            self.train_dataloader = torch.utils.data.DataLoader(dataserver_train,
                        batch_size=self.dl_studio.batch_size,shuffle=True, num_workers=2)
            self.test_dataloader = torch.utils.data.DataLoader(dataserver_test,
                               batch_size=self.dl_studio.batch_size,shuffle=False, num_workers=2)

        class TEXTnetWithEmbeddings(nn.Module):
            """
            This is embeddings version of the class TEXTnet class shown previously.  Since we
            are using the word2vec embeddings, we know that the input size for each word vector 
            will be a constant value of 300.  Overall, though, this network is meant for semantic 
            classification of variable-length sentiment data.  Based on my limited testing, the 
            performance of this network is very poor because it has no protection against 
            vanishing gradients when used in an RNN.  

            Class Path:  DLStudio -> TextClassificationWithEmbeddings -> TEXTnetWithEmbeddings
            """
            def __init__(self, input_size, hidden_size, output_size):
                super(DLStudio.TextClassificationWithEmbeddings.TEXTnetWithEmbeddings, self).__init__()
                self.input_size = input_size
                self.hidden_size = hidden_size
                self.output_size = output_size
                self.combined_to_hidden = nn.Linear(input_size + hidden_size, hidden_size)
                self.combined_to_middle = nn.Linear(input_size + hidden_size, 100)
                self.middle_to_out = nn.Linear(100, output_size)     
                self.logsoftmax = nn.LogSoftmax(dim=1)

            def forward(self, input, hidden):
                combined = torch.cat((input, hidden), 1)
                hidden = self.combined_to_hidden(combined)
                hidden = torch.tanh(hidden)                     
                out = self.combined_to_middle(combined)
                out = nn.functional.relu(out)
                out = self.middle_to_out(out)
                out = self.logsoftmax(out)
                return out,hidden         

            def init_hidden(self):
                hidden = torch.zeros(1, self.hidden_size)
                return hidden


        class TEXTnetOrder2WithEmbeddings(nn.Module):
            """
            This is an embeddings version of the TEXTnetOrder2 class shown previously.
            With the embeddings, we know that the size the tensor for word will be 300.
            As to how TEXTnetOrder2 differs from TEXTnet, the value of hidden as used at
            each time step also includes its value at the previous time step.  This 
            fact, not directly apparent by the definition of the class shown below, 
            is made possible by the last parameter, cell, in the header of forward().  
            All you can see here, at the end of forward(), is that the value of cell 
            goes through a linear layer and through a sigmoid nonlinearity. By the way, 
            since the sigmoid saturates at 0 and 1, it can act like a switch. Later 
            when I use this class in the training function, you will see the cell
            values being used in such a manner that the hidden state at each time
            step is mixed with the hidden state at the previous time step.

            Class Path:  DLStudio -> TextClassificationWithEmbeddings -> TEXTnetOrder2WithEmbeddings
            """
            def __init__(self, hidden_size, output_size, input_size=300):
                super(DLStudio.TextClassificationWithEmbeddings.TEXTnetOrder2WithEmbeddings, self).__init__()
                self.input_size = input_size
                self.hidden_size = hidden_size
                self.output_size = output_size
                self.combined_to_hidden = nn.Linear(input_size + 2*hidden_size, hidden_size)
                self.combined_to_middle = nn.Linear(input_size + 2*hidden_size, 100)
                self.middle_to_out = nn.Linear(100, output_size)     
                self.logsoftmax = nn.LogSoftmax(dim=1)
                self.dropout = nn.Dropout(p=0.1)
                # for the cell
                self.linear_for_cell = nn.Linear(hidden_size, hidden_size)

            def forward(self, input, hidden, cell):
                combined = torch.cat((input, hidden, cell), 1)
                hidden = self.combined_to_hidden(combined)
                hidden = torch.tanh(hidden)                     
                out = self.combined_to_middle(combined)
                out = nn.functional.relu(out)
                out = self.dropout(out)
                out = self.middle_to_out(out)
                out = self.logsoftmax(out)
                hidden_clone = hidden.clone()
#                cell = torch.tanh(self.linear_for_cell(hidden_clone))
                cell = torch.sigmoid(self.linear_for_cell(hidden_clone))
                return out,hidden,cell         

            def initialize_cell(self):
                weight = next(self.linear_for_cell.parameters()).data
                cell = weight.new(1, self.hidden_size).zero_()
                return cell

            def init_hidden(self):
                hidden = torch.zeros(1, self.hidden_size)
                return hidden


        class GRUnetWithEmbeddings(nn.Module):
            """
            For this embeddings adapted version of the GRUnet shown earlier, we can assume that
            the 'input_size' for a tensor representing a word is always 300.
            Source: https://blog.floydhub.com/gru-with-pytorch/
            with the only modification that the final output of forward() is now
            routed through LogSoftmax activation. 

            Class Path:  DLStudio -> TextClassificationWithEmbeddings -> GRUnetWithEmbeddings 
            """
            def __init__(self, input_size, hidden_size, output_size, num_layers=1): 
                """
                -- input_size is the size of the tensor for each word in a sequence of words.  If you word2vec
                       embedding, the value of this variable will always be equal to 300.
                -- hidden_size is the size of the hidden state in the RNN
                -- output_size is the size of output of the RNN.  For binary classification of 
                       input text, output_size is 2.
                -- num_layers creates a stack of GRUs
                """
                super(DLStudio.TextClassificationWithEmbeddings.GRUnetWithEmbeddings, self).__init__()
                self.input_size = input_size
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.gru = nn.GRU(input_size, hidden_size, num_layers)
                self.fc = nn.Linear(hidden_size, output_size)
                self.relu = nn.ReLU()
                self.logsoftmax = nn.LogSoftmax(dim=1)
                
            def forward(self, x, h):
                out, h = self.gru(x, h)
                out = self.fc(self.relu(out[:,-1]))
                out = self.logsoftmax(out)
                return out, h

            def init_hidden(self):
                weight = next(self.parameters()).data
                #                  num_layers  batch_size    hidden_size
                hidden = weight.new(  2,          1,         self.hidden_size    ).zero_()
                return hidden

        def save_model(self, model):
            "Save the trained model to a disk file"
            torch.save(model.state_dict(), self.dl_studio.path_saved_model)


        def run_code_for_training_with_TEXTnet_word2vec(self, net, display_train_loss=False):        
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net = copy.deepcopy(net)
            net = net.to(self.dl_studio.device)
            ## Note that the TEXTnet and TEXTnetOrder2 both produce LogSoftmax output. So we
            ## use nn.NLLLoss. The combined effect of LogSoftMax and NLLLoss is the same as 
            ## for the CrossEntropyLoss
            criterion = nn.NLLLoss()
            accum_times = []
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            start_time = time.perf_counter()
            training_loss_tally = []
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    hidden = net.init_hidden().to(self.dl_studio.device)              
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    sentiment = sentiment.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    input = torch.zeros(1,review_tensor.shape[2]).to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden = net(input, hidden)
                    loss = criterion(output, torch.argmax(sentiment,1))
                    running_loss += loss.item()
                    loss.backward(retain_graph=True)        
                    optimizer.step()
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss)
                        running_loss = 0.0
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%d  iter:%4d  elapsed_time: %4d secs]     loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                        accum_times.append(current_time-start_time)
                        FILE.write("%.3f\n" % avg_loss)
                        FILE.flush()
            print("\nFinished Training\n\n")
            self.save_model(net)
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
#                plt.legend()
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()


        def run_code_for_training_with_TEXTnetOrder2_word2vec(self, net, display_train_loss=False):        
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net = copy.deepcopy(net)
            net.to(self.dl_studio.device)
            ## Note that the TEXTnet and TEXTnetOrder2 both produce LogSoftmax output:
            criterion = nn.NLLLoss()
            accum_times = []
            optimizer = optim.SGD(net.parameters(), 
                                       lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            start_time = time.perf_counter()
            training_loss_tally = []
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    cell_prev = net.initialize_cell().to(self.dl_studio.device)
                    cell_prev_2_prev = net.initialize_cell().to(self.dl_studio.device)
                    hidden = net.init_hidden().to(self.dl_studio.device)              
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    sentiment = sentiment.to(self.dl_studio.device)
                    optimizer.zero_grad()
                    input = torch.zeros(1,review_tensor.shape[2])
                    input = input.to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden, cell = net(input, hidden, cell_prev_2_prev)
                        if k == 0:
                            cell_prev = cell
                        else:
                            cell_prev_2_prev = cell_prev
                            cell_prev = cell
                    loss = criterion(output, torch.argmax(sentiment,1))
                    running_loss += loss.item()
                    loss.backward()        
                    optimizer.step()
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss)
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%d  iter:%4d  elapsed_time: %4d secs]     loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                        accum_times.append(current_time-start_time)
                        FILE.write("%.3f\n" % avg_loss)
                        FILE.flush()
                        running_loss = 0.0
            print("\nFinished Training\n")
            self.save_model(net)
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
#                plt.legend()
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()


        def run_code_for_training_for_text_classification_with_GRU_word2vec(self, net, display_train_loss=False): 
            filename_for_out = "performance_numbers_" + str(self.dl_studio.epochs) + ".txt"
            FILE = open(filename_for_out, 'w')
            net = copy.deepcopy(net)
            net = net.to(self.dl_studio.device)
            ##  Note that the GRUnet now produces the LogSoftmax output:
            criterion = nn.NLLLoss()
            accum_times = []
            optimizer = optim.SGD(net.parameters(), 
                         lr=self.dl_studio.learning_rate, momentum=self.dl_studio.momentum)
            training_loss_tally = []
            start_time = time.perf_counter()
            for epoch in range(self.dl_studio.epochs):  
                print("")
                running_loss = 0.0
                for i, data in enumerate(self.train_dataloader):    
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    sentiment = sentiment.to(self.dl_studio.device)
                    ## The following type conversion needed for MSELoss:
                    ##sentiment = sentiment.float()
                    optimizer.zero_grad()
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        output, hidden = net(torch.unsqueeze(torch.unsqueeze(review_tensor[0,k],0),0), hidden)
                    loss = criterion(output, torch.argmax(sentiment, 1))
                    running_loss += loss.item()
                    loss.backward()
                    optimizer.step()
                    if i % 200 == 199:    
                        avg_loss = running_loss / float(200)
                        training_loss_tally.append(avg_loss)
                        current_time = time.perf_counter()
                        time_elapsed = current_time-start_time
                        print("[epoch:%d  iter:%4d  elapsed_time:%4d secs]     loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                        accum_times.append(current_time-start_time)
                        FILE.write("%.5f\n" % avg_loss)
                        FILE.flush()
                        running_loss = 0.0
            self.save_model(net)
            print("Total Training Time: {}".format(str(sum(accum_times))))
            print("\nFinished Training\n\n")
            if display_train_loss:
                plt.figure(figsize=(10,5))
                plt.title("Training Loss vs. Iterations")
                plt.plot(training_loss_tally)
                plt.xlabel("iterations")
                plt.ylabel("training loss")
#                plt.legend()
                plt.legend(["Plot of loss versus iterations"], fontsize="x-large")
                plt.savefig("training_loss.png")
                plt.show()


        def run_code_for_testing_with_TEXTnet_word2vec(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            net.to(self.dl_studio.device)
            classification_accuracy = 0.0
            negative_total = 0
            positive_total = 0
            confusion_matrix = torch.zeros(2,2)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    review_tensor = review_tensor.to(self.dl_studio.device)
                    category      = category.to(self.dl_studio.device)
                    sentiment     = sentiment.to(self.dl_studio.device)
                    input = torch.zeros(1,review_tensor.shape[2]).to(self.dl_studio.device)
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden = net(input, hidden)
                    predicted_idx = torch.argmax(output).item()
                    gt_idx = torch.argmax(sentiment).item()
                    if i % 100 == 99:
                        print("   [i=%4d]    predicted_label=%d       gt_label=%d" % (i+1, predicted_idx,gt_idx))
                    if predicted_idx == gt_idx:
                        classification_accuracy += 1
                    if gt_idx == 0: 
                        negative_total += 1
                    elif gt_idx == 1:
                        positive_total += 1
                    confusion_matrix[gt_idx,predicted_idx] += 1
            print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
            out_percent = np.zeros((2,2), dtype='float')
            out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
            out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
            out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
            out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
            print("\n\nNumber of positive reviews tested: %d" % positive_total)
            print("\n\nNumber of negative reviews tested: %d" % negative_total)
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                      "
            out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
            print(out_str + "\n")
            for i,label in enumerate(['true negative', 'true positive']):
                out_str = "%12s%%:  " % label
                for j in range(2):
                    out_str +=  "%18s%%" % out_percent[i,j]
                print(out_str)


        def run_code_for_testing_with_TEXTnetOrder2_word2vec(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            net.to(self.dl_studio.device)
            classification_accuracy = 0.0
            negative_total = 0
            positive_total = 0
            confusion_matrix = torch.zeros(2,2)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    cell_prev = net.initialize_cell()
                    cell_prev_2_prev = net.initialize_cell()
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    input = torch.zeros(1,review_tensor.shape[2]).to(self.dl_studio.device)
                    hidden = net.init_hidden().to(self.dl_studio.device)
                    for k in range(review_tensor.shape[1]):
                        input[0,:] = review_tensor[0,k]
                        output, hidden, cell = net(input, hidden, cell_prev_2_prev)
                        if k == 0:
                            cell_prev = cell
                        else:
                            cell_prev_2_prev = cell_prev
                            cell_prev = cell
                    predicted_idx = torch.argmax(output).item()
                    gt_idx = torch.argmax(sentiment).item()
                    if i % 100 == 99:
                        print("   [i=%4d]    predicted_label=%d       gt_label=%d" % (i+1, predicted_idx,gt_idx))
                    if predicted_idx == gt_idx:
                        classification_accuracy += 1
                    if gt_idx == 0: 
                        negative_total += 1
                    elif gt_idx == 1:
                        positive_total += 1
                    confusion_matrix[gt_idx,predicted_idx] += 1
            print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
            out_percent = np.zeros((2,2), dtype='float')
            out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
            out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
            out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
            out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
            print("\n\nNumber of positive reviews tested: %d" % positive_total)
            print("\n\nNumber of negative reviews tested: %d" % negative_total)
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                      "
            out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
            print(out_str + "\n")
            for i,label in enumerate(['true negative', 'true positive']):
                out_str = "%12s:  " % label
                for j in range(2):
                    out_str +=  "%18s" % out_percent[i,j]
                print(out_str)


        def run_code_for_testing_text_classification_with_GRU_word2vec(self, net):
            net.load_state_dict(torch.load(self.dl_studio.path_saved_model))
            classification_accuracy = 0.0
            negative_total = 0
            positive_total = 0
            confusion_matrix = torch.zeros(2,2)
            with torch.no_grad():
                for i, data in enumerate(self.test_dataloader):
                    review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
                    hidden = net.init_hidden()
                    for k in range(review_tensor.shape[1]):
                        output, hidden = net(torch.unsqueeze(torch.unsqueeze(review_tensor[0,k],0),0), hidden)
                    predicted_idx = torch.argmax(output).item()
                    gt_idx = torch.argmax(sentiment).item()
                    if i % 100 == 99:
                        print("   [i=%d]    predicted_label=%d       gt_label=%d" % (i+1, predicted_idx,gt_idx))
                    if predicted_idx == gt_idx:
                        classification_accuracy += 1
                    if gt_idx == 0: 
                        negative_total += 1
                    elif gt_idx == 1:
                        positive_total += 1
                    confusion_matrix[gt_idx,predicted_idx] += 1
            print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
            out_percent = np.zeros((2,2), dtype='float')
            out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
            out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
            out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
            out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
            print("\n\nNumber of positive reviews tested: %d" % positive_total)
            print("\n\nNumber of negative reviews tested: %d" % negative_total)
            print("\n\nDisplaying the confusion matrix:\n")
            out_str = "                      "
            out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
            print(out_str + "\n")
            for i,label in enumerate(['true negative', 'true positive']):
                out_str = "%12s:  " % label
                for j in range(2):
                    out_str +=  "%18s%%" % out_percent[i,j]
                print(out_str)


#_________________________  End of DLStudio Class Definition ___________________________

#______________________________    Test code follows    _________________________________

if __name__ == '__main__': 
    pass
