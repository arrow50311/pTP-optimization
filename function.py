####################################################################################
# This script will help calculate the pTPr according to Gerhard Hummer's Bayesian 
# formula; It has been compressed into a f function;
#
# Written by Xingcheng Lin, 12/12/2016
####################################################################################

import math;
import subprocess;
import os;
import shutil;
import math;
import numpy as np;
import time;

################################################
def my_lt_range(start, end, step):
    while start < end:
        yield start
        start += step

def my_le_range(start, end, step):
    while start <= end:
        yield start
        start += step
###########################################

def function( weight_vector, *args ):

    # Check and copy the existence of a file, and make copy;
    for i in my_lt_range(1, 1000000, 1):
        targetFile = "backup/weight." + str(i) + ".txt";
        if (os.path.isfile(targetFile)):
            pass;
        else:
            src = "tmp_weight.txt";
            shutil.copy(src, targetFile);
            break;
    
    # Reshape matrix back;
    nRow=int(subprocess.check_output("wc -l ../qimap.out | cut -f1 -d' '", shell=True));
    nCol = len(weight_vector);

    matrix = np.reshape(args, (nRow, nCol));


    # Multiply the matrix with its corresponding weight, add up to be the weighted Q;
    weighted_Q = np.dot(matrix, weight_vector);

    # Find the maximum and minimum value of weighted_Q values; They will be the boundaries of Q values;
    weightedQ_max = np.amax(weighted_Q);
    weightedQ_min = np.amin(weighted_Q);

    # Do feature scaling to weighted Q to be in between 0 and 1;
    weighted_Q_norm = (weighted_Q - weightedQ_min) / (weightedQ_max - weightedQ_min);

    outfile = open("Q.out", "w");

    for i in my_lt_range(0, len(weighted_Q_norm), 1):
        outfile.write(str(i) + "\t" + str(weighted_Q_norm[i]) + "\n");

    outfile.close();
    

    # Calculate the free energy plot;
    topRC = 1.0;
    bottomRC = 0.0;
    stepRC = 0.01; # We decided to have 100 number of bins;
    inputName = "Q.out";
    output1Name = "histQ.txt";
    output2Name = "histQ_smooth.txt";
    output3Name = "FvQ.txt";

    paramList = [topRC, bottomRC, stepRC, inputName, output1Name, output2Name, output3Name];

    from fenergy import fenergy
    fenergy( paramList );

    from findHistMin import findHistMin
    peakList = findHistMin();

    print peakList;

    # Calculate for Transition path ensemble;
    from findTP import findTP
    findTP( peakList );

    # Sort according to the first column so that the time will keep increasing;
    # This is because findTP.py does not output in a increasing-time manner;
    subprocess.call("sort -s -n -k 1,1 TPtime.xvg > TPtime.sort.xvg", shell=True);

    # Get QTP files;
    subprocess.call("paste Q.out TPtime.sort.xvg | awk '{if($4==1)print $1,$2}'>QTP.out", shell=True);

    
    # Calculate Q for TP.xtc

#    # Calculate p(TP);
    no=float(subprocess.check_output("wc -l Q.out | cut -f1 -d' '", shell=True));
    no_TP=float(subprocess.check_output("wc -l QTP.out | cut -f1 -d' '", shell=True));

    print (no, no_TP);

#    # Calculate P(r) and P(r|TP);
    inputName = "QTP.out";
    output1Name = "histQ_TP.txt";
    output2Name = "histQ_TP_smooth.txt";
    output3Name = "FvQ_TP.txt";

    paramList = [topRC, bottomRC, stepRC, inputName, output1Name, output2Name, output3Name];
    fenergy( paramList );

    # Finally, invoke the Bayesian equation to evaluate P(TP|r);
    subprocess.call("paste histQ_TP.txt histQ.txt | awk -v var1='%d' -v var2='%d' '{if($4 != 0)print $1,$2*var2/var1/$4}'>pTPr.txt" %(no, no_TP), shell=True)

    # Take the largest number of pTPr and return;
    infile = open("pTPr.txt", "r");
    matrix = [line.strip().split() for line in infile];
    infile.close();
    length = len(matrix);
    maxPTPr = 0.0;

    for i in my_lt_range(0, length, 1):
        tmp = float(matrix[i][1]);
        if (tmp > maxPTPr):
            maxPTPr = tmp;
           
    outfile_weight = open("tmp_weight.txt", "w");

    for i in my_lt_range(0, len(weight_vector), 1):
        outfile_weight.write(str(weight_vector[i]) + "\n");

    outfile_weight.write("The best pTPr is:" + "\n" + str(maxPTPr) + "\n");
    outfile_weight.close();

    return -1*maxPTPr;

############################################################################
print "Love is an endless mystery,"
print "for it has nothing else to explain it."

