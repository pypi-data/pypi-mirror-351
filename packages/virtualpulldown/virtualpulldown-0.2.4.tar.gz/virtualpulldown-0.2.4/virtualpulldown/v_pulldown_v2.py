#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import subprocess
from Bio import Entrez, SeqIO
from openpyxl import Workbook
from time import sleep
from argparse import ArgumentParser

"""
Usage:        ./v_pulldown_v2.py <template.xlsx>
Author:       Heewhan Shin
Author_email: hshin40@gmail.com
Date:         April 28, 2023
"""

def parse_arguments():
    parser = ArgumentParser(description="Process genomic sequences and pair bait with prey sequences.")
    parser.add_argument("contig_file", nargs="?", help="Excel file with accession IDs e.g. <template.xlsx>")
    parser.add_argument("--email", default=os.getenv("NCBI_EMAIL", "user@example.com"), help="Email for NCBI Entrez")
    return parser.parse_args()

def download_nucleotide_sequence(contig_id, email, retries=3, delay=1):
    Entrez.email = email
    for attempt in range(retries):
        try:
            handle = Entrez.efetch(db="nucleotide", id=contig_id, rettype="fasta", retmode="text")
            data = handle.read()
            handle.close()
            lines = data.split('\n')
            if not lines[0].strip():
                return None
            return '\n'.join([lines[0]] + [''.join(lines[1:])])
        except Exception as e:
            print(f"Error downloading {contig_id}: {e}. Retrying {attempt+1}/{retries}...")
            sleep(delay)
    print(f"Failed to download {contig_id} after {retries} attempts.")
    return None

def run_prodigal(input_filepath, output_filepath):
    try:
        result = subprocess.run(
            ["prodigal", "-p", "meta", "-i", input_filepath, "-a", output_filepath],
            capture_output=True, text=True, check=True
        )
        print(f"Prodigal annotation completed for {input_filepath}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Prodigal annotation failed for {input_filepath}: {e.stderr}")
        return False

def create_master_table(contig_id, faa_file, output_dir):
    wb = Workbook()
    ws = wb.active
    ws.append(['Locus_tag', 'sequence', 'Gene_length', 'start', 'end'])
    
    try:
        for record in SeqIO.parse(faa_file, 'fasta'):
            locus_tag = record.id.split('_')[-1]
            seq = str(record.seq)
            gene_length = len(seq) - 1  # Adjust for stop codon
            start, end = map(int, record.description.split('#')[1:3])
            ws.append([locus_tag, seq, gene_length, start, end])
        wb.save(os.path.join(output_dir, f"{contig_id}_master.xlsx"))
        print(f"Master table saved: log/{contig_id}_master.xlsx")
    except Exception as e:
        print(f"Error creating master table for {contig_id}: {e}")

def main():
    args = parse_arguments()
    contig_file = args.contig_file or input("Please specify the file containing accession IDs (ex: temp.xlsx): ")
    user_input = input("Check annotation first (1) or Ready to pair sequences? (2): ").lower()
    
    if not os.path.exists(contig_file):
        print(f"Error: {contig_file} does not exist.")
        sys.exit(1)
    
    for d in ["fa", "ready", "seq_data", "seq_annotated", "log"]:
        os.makedirs(d, exist_ok=True)
    
    try:
        df = pd.read_excel(contig_file)
    except Exception as e:
        print(f"Error reading {contig_file}: {e}")
        sys.exit(1)
    
    for _, row in df.iterrows():
        contig_id = row['Assembly_Accession']
        if pd.notna(contig_id):
            seq = download_nucleotide_sequence(contig_id, args.email)
            if seq:
                with open(f"seq_data/{contig_id}_nucleotide.fasta", 'w') as f:
                    f.write(seq)
    
    for filename in os.listdir("seq_data"):
        if filename.endswith("_nucleotide.fasta"):
            contig_id = filename.replace("_nucleotide.fasta", "")
            input_filepath = os.path.join("seq_data", filename)
            output_filepath = os.path.join("seq_annotated", f"{contig_id}_proteins.faa")
            run_prodigal(input_filepath, output_filepath)
    
    for filename in os.listdir("seq_annotated"):
        if filename.endswith("_proteins.faa"):
            contig_id = filename.replace("_proteins.faa", "")
            create_master_table(contig_id, os.path.join("seq_annotated", filename), "log")
    
    if user_input == '2':
        for _, row in df.iterrows():
            contig_id = row['Assembly_Accession']
            if pd.notna(contig_id):
                try:
                    start_id = int(row['start_id'])
                    end_id = int(row['end_id'])
                    bait_seq = row['bait_seq']
                except (ValueError, KeyError) as e:
                    print(f"Invalid data for {contig_id}: {e}")
                    continue
                
                for d in [f"fa/{contig_id}", f"ready/{contig_id}", f"log/{contig_id}"]:
                    os.makedirs(d, exist_ok=True)
                
                faa_file = f"seq_annotated/{contig_id}_proteins.faa"
                if os.path.exists(faa_file):
                    for record in SeqIO.parse(faa_file, 'fasta'):
                        prey_id = int(record.id.split('_')[-1])
                        if start_id <= prey_id <= end_id:
                            prey_seq = str(record.seq).split('*')[0]
                            header = record.id
                            with open(f"fa/{contig_id}/{header}.fa", 'w') as f:
                                f.write(f">{header}\n{prey_seq}\n")
                            with open(f"ready/{contig_id}/{header}_paired.fasta", 'w') as f:
                                f.write(f">{header}\n{bait_seq}:{prey_seq}\n")
                            with open(f"log/{contig_id}/range.dat", 'w') as f:
                                f.write(f"{start_id} {end_id}\n")
                            with open(f"log/{contig_id}/pairing.log", 'w') as f:
                                f.write(f"pairing {contig_id} bait sequence to prey sequences found between {start_id} and {end_id}...\n")
                                f.write(f"bait sequence = {bait_seq}\n")
                    print(f"Processed {contig_id}: prey (in fa) and paired files (in ready) saved.")

if __name__ == "__main__":
    main()
