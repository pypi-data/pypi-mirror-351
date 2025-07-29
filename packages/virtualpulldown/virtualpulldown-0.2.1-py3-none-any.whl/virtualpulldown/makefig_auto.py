#!/usr/bin/env python
"""
Usage:        ./makefig_auto.py
Author:       Heewhan Shin
Author_email: hshin40@gmail.com
Date:         April 28, 2023
Description:  This script extracts pTM and ipTM values from output files and produces a scatter plot and concatenate all PAE plots.
"""
def main():
    import subprocess
    import os
    import sys
    from run import concatenate_images, plot_ptm_iptm, convert_to_pdf, rename_files

    ## Specify inputs
    path            = "./"                  # Working directory
    title_offset    = 2                     # Adjust location of the title
    f_width         = 12                    # Figure width
    f_height        = 5                     # Figure height
    fontsize        = 10                    # Font size
    margin_top      = 15
    margin_bot      = 10
    margin_left     = 10
    margin_right    = 15
    key_position    = 'left'                # Position of legend

    if len(sys.argv) > 1:
        bait_name = sys.argv[1]
    else:
        bait_name = input("Please specify the title (ex: SPBeta): ")

    rename_files(path)
    print("files are renamed using locus_tags...")

    figures = [f"{bait_name}.eps", f"{bait_name}_pae.png"]

    if os.path.isfile(f"{bait_name}_pae.png"):
        print(f"Concatenated {bait_name}_pae figure already exists..")
        print("Stopping process. Please check the figure..")
        exit(1)

    # Making PAE plots
    result = concatenate_images(path)
    result.save(f"{bait_name}_pae.png")

    subprocess.call("echo pae plots are concatenated...", shell=True)
    subprocess.call("echo plotting pTM and iPTM values...\n", shell=True)

    # Plotting pTM and ipTM data
    plot_ptm_iptm(bait_name, title_offset, path, f_width, f_height, fontsize,
                  margin_top, margin_bot, margin_left, margin_right, key_position)
    subprocess.call("echo pTM, iPTM values are plotted...\n", shell=True)
    subprocess.call("echo converting eps to pdf...", shell=True)

    # Converting figures to pdf
    convert_to_pdf(figures)

if __name__ == "__main__":
    main()

