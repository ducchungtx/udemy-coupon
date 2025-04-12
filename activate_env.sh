#!/bin/bash
# Script to activate the Conda environment for the Udemy coupon project

# Ensure conda is properly initialized
source $(conda info --base)/etc/profile.d/conda.sh

# Activate the environment
conda activate udemy-coupon

# Print confirmation message
echo "Udemy coupon environment activated! You can now run the application with:"
echo "python main.py"