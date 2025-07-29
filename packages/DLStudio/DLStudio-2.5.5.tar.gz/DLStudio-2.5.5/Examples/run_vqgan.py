#!/usr/bin/env python

##  run_vqgan.py

"""
Note that the following two scripts in the Examples directory

              run_vqgan.py                              (this script file)

              run_vqgan_transformer.py

have a paired existence in DLStudio.  You MUST run both of these script if you want
to experiment with what a VQGAN is meant for: For autoregressive modeling of images
with the tokens that consist of the codebook vectors.  In general,

  ---  First, you train the VQGAN network for learning the Codebook, while, obviously also
       learning the VQGAN Encoder and the Decoder.  This is accomplished by the script

              run_vqgan.py

       in the Examples directly.  This is the script file you are looking at now.

       Execute this script for a couple of epochs just to make sure that all is okay with 
       your installation of the code.  Subsequently, run the script for a couple of hundred 
       epochs for training well the Codebook.

  ---  Subsequently, you need to train the Transformer part of the the VQGAN by running
       the following script:

            run_vqgan_transformer.py

       which is also in the Examples directory.  Run it initially for, say, around 10
       epochs and see what sort of results you get with Transformer based modeling 
       of the codebook integer sequences that represent the input images.  Each integer
       is the index of the codebook vector.  Initially, these sequences correspond to
       the Latent Space representation of an created by the Encoder.  If NxNxC is the
       shape of the output of the Encoder, you can think of this output as a sequence
       of N^2 embedding vectors of size C and create a transformer based prediction 
       network for such sequences.

About the overall organization of the VQGAN code in DLStudio, note that it is a part of 
an inheritance hierarchy rooted at the Autoencoder class:

                            Autoencoder
                                |
                                |
                                v
                               VAE
                                |
                                |
                                v
                              VQVAE
                                |
                                |
                                v
                              VQGAN

The root class Autoencoder supplies all the functionality that is needed by all the 
classes in the hierarchy, the most important being the Encoder and the Decoder classes.
This classes are designed using Skip Blocks in such a way that you can them arbitrarily
deep by specifying the number of repetitions of a Skip Block that has the same number
of channels going on and coming out.

As you can imagine, the other classes in the hierarchy provide the more specialized 
behaviors that you would expect from those.  In particular, variational autoencoding 
with the codebook learning behavior is first provided VQVAE that stands for 
"Vector Quantizer -- Variational Auto Encoding".  Subsequently, a more modern 
incarnation of the same is provided in VQGAN in which Adversarial Learning as made
possible by a GAN is used to train the Encoder/Decoder part of the Variational
Autoencoder. As is the case with a VQGAN, after you train the Encoder/Decoder part
of the overall network, you then use a transformer for autoregressive modeling of the
codebook sequences for the images in your training dataset.
                            
Execute this script by calling


1.           python3  run_vqgan.py

Do not forget that after you have run the script in the current file, you must also
run the following script:

             2.     python3  run_vqgan_transformer.py

for training the transformer for autoregressive modeling of the Codebook indices
put out by the Vector Quantizer in a VQGAN.

"""


"""
seed = 0           
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
numpy.random.seed(seed)
torch.backends.cudnn.deterministic=True
torch.backends.cudnn.benchmarks=False
os.environ['PYTHONHASHSEED'] = str(seed)
"""

##  watch -d -n 0.5 nvidia-smi

from DLStudio import *
import os, sys


#dataroot = "./dataGAN/PurdueShapes5GAN/multiobj/"
#dataroot =  "/home/kak/ImageDatasets/PurdueShapes5GAN/multiobj/"
#dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/PurdueShapes5GAN/multiobj/"
#dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/flowers/jpg/"
dataroot = "/mnt/cloudNAS3/Avi/ImageDatasets/flowers/"

#use_patch_gan_logic = False
use_patch_gan_logic = True

#epochs = 2          ## for debugging
#epochs = 50
epochs = 100

batch_size = 48       ## for debugging   
#batch_size = 16      ## for debugging   
#batch_size = 128     ##  for more serious work

## Repetitions of the skip blocks in the Encoder and Decoder networks. These are
## the skip blocks for which the number of input channels equals the number of 
## output channels:
num_repeats = 10

learning_rate = 1e-4
#learning_rate = 1e-5

## The dataset images:
image_size = (64,64)                


## Specifying the size of the images reconstructed by the Decoder:
decoder_out_size = (64,64)


########################################################################
##  The following three Choices are combined selections:

##  Choice 1:
encoder_out_size = (8,8)
encoder_out_ch  = 512                     ##  when encoder_out_size = (8,8)
codebook_vec_dim  = 512                   ##  Must be the same as "encoder_out_ch"

##  Choice 2:
#encoder_out_size = (16,16)
#encoder_out_ch  = 256                        ## when encoder_out_size = (16,16)
#codebook_vec_dim  = 256                      ##  Must be the same as "encoder_out_ch"

##  Choice 3:
#encoder_out_size = (32,32)
#encoder_out_ch  = 128                       ## when encoder_out_size = (32,32)
#codebook_vec_dim  = 128                     ##  Must be the same as "encoder_out_ch"
########################################################################



## Specifying the Codebook size:
#
#num_codebook_vecs = 512       
num_codebook_vecs = 256       
#num_codebook_vecs = 128       
#num_codebook_vecs = 64
#num_codebook_vecs = 32
                              

## For calculating the vector-quantization losses:
commitment_cost = 0.25
decay = 0.99
#perceptual_loss_factor =  2.5
perceptual_loss_factor =  1.2
#perceptual_loss_factor =  20

dls = DLStudio(
                  dataroot = dataroot,
                  image_size = image_size,
                  learning_rate = learning_rate,        
                  epochs = epochs,
                  batch_size = batch_size,
                  use_gpu = True,
              )


vqgan  =  DLStudio.VQGAN( 
                       dl_studio = dls,
                       encoder_in_im_size = image_size,
                       encoder_out_im_size = encoder_out_size,
                       decoder_out_im_size = decoder_out_size,
                       encoder_out_ch = encoder_out_ch,
                       num_repeats = num_repeats,
                       num_codebook_vecs = num_codebook_vecs,
                       codebook_vec_dim = codebook_vec_dim, 
                       commitment_cost = commitment_cost, 
                       decay = decay,
                       perceptual_loss_factor = perceptual_loss_factor,
                       use_patch_gan_logic = use_patch_gan_logic,
                       path_saved_generator = "./saved_VQGAN_generator",
                    )
          

#number_of_learnable_params_in_vqgan = sum(p.numel() for p in vqgan.parameters() if p.requires_grad)
#print("\n\nThe number of learnable parameters in VQGAN: %d" % number_of_learnable_params_in_vqgan)

vqgan.set_dataloader()

if use_patch_gan_logic is True:
    vqgan.run_code_for_PATCH_BASED_training_VQGAN( vqgan )   
else:
    vqgan.run_code_for_training_VQGAN( vqgan )   

vqgan.run_code_for_evaluating_VQGAN(vqgan, visualization_dir = "vqgan_visualization_dir")

