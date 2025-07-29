#!/usr/bin/env python
"""
Usage:        ./makefig_auto.py
Author:       Heewhan Shin
Author_email: hshin40@gmail.com
Date:         April 28, 2023
Description:  This script extracts pTM and ipTM values from output files and produces a scatter plot and concatenate all PAE plots.
"""
from run import concatenate_images, plot_ptm_iptm, convert_to_pdf, rename_files
import subprocess
import os
import argparse
import sys

## Specify inputs
###########################################################
path            = "./"                  #Working directory
title_offset    = 2                     #Change number to adjust location of the title
f_width         = 12                    #Figure width
f_height        = 5                     #Figure height
fontsize        = 10                    #Decrease the font and figure sizes or margins to fit a plot in a white space 
margin_top      = 15                    
margin_bot      = 10 
margin_left     = 10
margin_right    = 15
key_position    = 'left'                # right, left, topleft, topright..etc
###########################################################

if len(sys.argv) > 1:
    bait_name=sys.argv[1]
else:
    bait_name= input("Please specify the title (ex: SPBeta): ")

rename_files(path)
print ("files are renamed using locus_tags...")

figures=['%s.eps'%(bait_name),'%s_pae.png'%(bait_name)]

if os.path.isfile("%s_pae.png"%(bait_name)):
    print("Concatenated %s_pae figure already exists.."%(bait_name))
    print("Stopping process. Please check the figure..")
    exit(1)

##making PAE plots
result = concatenate_images(path)
result.save('%s_pae.png'%(bait_name))

subprocess.call("echo pae plots are concatenated...", shell=True)
subprocess.call("echo plotting pTM and iPTM values...\n", shell=True)

##plotting ptm and iptm data
plot_ptm_iptm(bait_name, title_offset, path, f_width, f_height, fontsize, margin_top, margin_bot, margin_left, margin_right, key_position)
subprocess.call("echo pTM, iPTM values are plotted...\n", shell=True)
subprocess.call("echo converting eps to pdf...",shell=True)

##converting figures to pdf
convert_to_pdf(figures)
