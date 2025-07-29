#!/usr/bin/env python

##  run_vqgan_map_image_to_codebook.py

"""
In order to play with this script, you must first run the script

            run_vqgan.py

to train the VQGAN network that consists of the Encoder, the Decoder, the Discrminator, and the
VectorQuantizer.

After the above learning, playing with the script in this file, that is, with

           run_vqgan_map_image_to_codebook.py

can provide you with deeper intuitions regarding what exactly is represented by the codebook
vectors.

Note that codebook learning, in general, erases the distinction between processing languages
(the same thing as text) and processing images.  Codebook learning is obviously a natural fit
for language processing because languages are serial structures and the most fundamental unit
in such a structure is a word (or a token as a subword). Once you have set the vocabulary for
the fundamental units, it automatically follows that any sentence would be expressible as a
sequence of the tokens and, consequently, as a sequence of the embedding vectors for the
tokens.

Codebook learning as made possible by VQGAN allows an automaton to understand images in exactly
the same manner as described above.  What a token vocabulary is for the case of languages is
the codebook learned by VQGAN for the case of images. The size of the codebook for VQGAN is set
by the user, as is the size of the token vocabulary for the case of languages. Subsequently,
each embedding vector at the output of the VQGAN Encode is replaced by the closest codebook
vector.

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

The DLStudio function invoked by this script is:

         encode_image_into_sequence_of_indices_to_codebook_vectors()

It is a method defined for the class VQGAN, which is an inner class of the main DLStudio class.

If the above function is called without an argument, the script will randomly choose a batch
of images and report results on the batch.   However, if you wish, you can invoke the function
on a single image.


To execute this script:

                 python3  run_vqgan_map_image_to_codebook.py

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

use_patch_gan_logic = False
#use_patch_gan_logic = True

epochs = 2          ## for debugging
#epochs = 40
#epochs = 15
#epochs = 50
#epochs = 100

batch_size = 48      ## for debugging   
#batch_size = 16      ## for debugging   
#batch_size = 128

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

          

number_of_learnable_params_in_vqgan = sum(p.numel() for p in vqgan.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in VQGAN: %d" % number_of_learnable_params_in_vqgan)

vqgan.set_dataloader()

##  Choose one of the rest of the statements:

## Try the following for a randomly selected batch:
vqgan.encode_image_into_sequence_of_indices_to_codebook_vectors()

## Try one of the following for a specific image:

##          Make sure you have named image files that bear some resemblance to the
##          dataset used for training the VQGAN network.

#vqgan.encode_image_into_sequence_of_indices_to_codebook_vectors( "image_04540.jpg" )
#vqgan.encode_image_into_sequence_of_indices_to_codebook_vectors( "image_08168.jpg" )

