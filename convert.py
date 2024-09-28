import subprocess
import struct
import esptool
import random


# create a list of filenames to load
filenames = [
	"Samples/instrument1.raw",
    "Samples/instrument2.raw",
    "Samples/instrument3.raw",
    "Samples/instrument4.raw",
    "Samples/instrument5.raw",
    "Samples/instrument6.raw",
    "Samples/instrument7.raw",
    "Samples/instrument8.raw",
    "Samples/instrument9.raw",
    "Samples/instrument10.raw",
    "Samples/instrument11.raw",
    "Samples/instrument12.raw"
]

filenamesDrums = [
    "Samples/kick1.raw",
    "Samples/snare1.raw",
    "Samples/special1.raw",
    "Samples/hihat1.raw",
    "Samples/kick2.raw",
    "Samples/snare2.raw",
    "Samples/special2.raw",
    "Samples/hihat2.raw",
    "Samples/kick3.raw",
    "Samples/snare3.raw",
    "Samples/special3.raw",
    "Samples/hihat3.raw"
]

filenamesSfx = [
    "Samples/sfx1.raw",
    "Samples/sfx2.raw",
    "Samples/sfx3.raw",
    "Samples/sfx4.raw",
    "Samples/sfx5.raw",
    "Samples/sfx6.raw",
    "Samples/sfx7.raw",
    "Samples/sfx8.raw",
    "Samples/sfx9.raw",
    "Samples/sfx10.raw",
    "Samples/sfx11.raw",
    "Samples/sfx12.raw"
]

import serial.tools.list_ports
comList = serial.tools.list_ports.comports()
howTouse = "\33[35mUse a sound editor that can save RAW files, such as Audacity (free)\n"
howTouse += "to overwrite files in the \"Samples\" dir.\n"
howTouse += "\33[32mExport files with following settings: Signed 16 bit PCM, 44100 Hz, Mono\n"
howTouse += "\33[35mRun this app to encode firmware image and upload to MothSynth\n"

print("\033[H\033[J")
print(howTouse)
print("************************************************************\n")
print("Select COM port MothSynth is connected to")
print("On Windows it will likely be called USB Serial Device")
print("On Mac it will likely be called USBMODEM# or USBSERIAL#")
print("\n************************************************************")
print("")

for i in range(0, len(comList)):
    print("{} : {} {} ".format( i,comList[i].device, comList[i].description))
    
#if comlist empty exit with error
if len(comList) == 0:
    print("No COM ports found, please connect MothSynth and try again")
    exit()
comPortIndex = int(input("Enter COM port index: "))
#validate
if comPortIndex < 0 or comPortIndex >= len(comList):
    print("Invalid COM port index")
    exit()
    
com = comList[comPortIndex].device
print("\033[H\033[J")
# load MothOS.bin.into file and convert to 64 bit integer list
# copy MothOS.bin to MothOS2.ino.bin
with open("MothOS.ino.bin", "rb") as f:
    MothOSCopy = f.read()
    with open("MothOS2.ino.bin", "wb") as f2:
        f2.write(MothOSCopy)

#$for loop 0 to 1
tempoIndex = 0
for encodeI in range(0, 3):
    
    # capture output into a variable
    result = subprocess.run(["python3", "-m", "esptool", "image_info", "MothOS2.ino.bin"], capture_output=True, text=True)
    output = result.stdout

    with open("MothOS2.ino.bin", "rb") as f:
        MothOS = f.read()
        #convert mothOS into int list
        MothOSInts = []
        for i in range(0, len(MothOS), 4):
            MothOSInts.append(struct.unpack("<i", MothOS[i:i+4])[0])

    # find integer value 31000 in MothOS and print it's index
    try:
        print("Modyfying image file...")
        #find 31000 and replace with 120
        tempoIndex = MothOSInts.index(31000)
        MothOSInts[tempoIndex] = 120
        tempoIndex = MothOSInts.index(31001)
        MothOSInts[tempoIndex] = 132
        tempoIndex = MothOSInts.index(31002)
        MothOSInts[tempoIndex] = 95
        tempoIndex = MothOSInts.index(31003)
        MothOSInts[tempoIndex] = 180
         
        #encode lenths of samples
        lI = 30001
        for i in range(1, 11):
            filename = filenames[i-1]
            sequence = [1, 2, 1, 3, 1, 4, 1, i]
            lengthIndex = MothOSInts.index(lI)
            sequenceIndex = 0
            for j in range(len(MothOSInts) - len(sequence)):
                if MothOSInts[j:j + len(sequence)] == sequence:
                    sequenceIndex = j
                    print("Encoding {}".format(filename))
                    #load filename and convert to signed 16 bit integers
                    with open(filename, "rb") as f:
                        sample = f.read()
                        sampleInts = []
                        for i in range(0, len(sample), 2):
                            sampleInts.append(struct.unpack("<h", sample[i:i+2])[0])
                       
                        #write random -3000,3000 to MothOSInts at sequenceIndex of sampleInts length
                        max = len(sampleInts)
                        
                        #limit max to 16000
                        if max > 44000:
                            max = 44000
                        for r in range(0, max):
                            MothOSInts[sequenceIndex+r] = sampleInts[r]
                
                    break
            lI += 1  
       
        for i in range(1, 13):
            filename = filenamesDrums[i-1]
            sequence = [2, 2, 1, 3, 1, 4, 1, i]
            sequenceIndex = 0
            for j in range(len(MothOSInts) - len(sequence)):
                if MothOSInts[j:j + len(sequence)] == sequence:
                    sequenceIndex = j
                    print("Encoding {}".format(filename))
                    #load filename and convert to signed 16 bit integers
                    with open(filename, "rb") as f:
                        sample = f.read()
                        sampleInts = []
                        for i in range(0, len(sample), 2):
                            sampleInts.append(struct.unpack("<h", sample[i:i+2])[0])
                       
                        #write random -3000,3000 to MothOSInts at sequenceIndex of sampleInts length
                        max = len(sampleInts)
                        
                        #limit max to 16000
                        if max > 16000:
                            max = 16000
                        for r in range(0, max):
                            MothOSInts[sequenceIndex+r] = sampleInts[r]
                
                    break
         
        for i in range(1, 13):
            filename = filenamesSfx[i-1]
            sequence = [3, 2, 1, 3, 1, 4, 1, i]
            sequenceIndex = 0
            for j in range(len(MothOSInts) - len(sequence)):
                if MothOSInts[j:j + len(sequence)] == sequence:
                    sequenceIndex = j
                    print("Encoding {}".format(filename))
                    #load filename and convert to signed 16 bit integers
                    with open(filename, "rb") as f:
                        sample = f.read()
                        sampleInts = []
                        max = len(sample)
                        for i in range(0, len(sample), 2):
                            sampleInts.append(struct.unpack("<h", sample[i:i+2])[0])
                       
                        max = len(sampleInts)
                        #limit max to 16000
                        if max > 16000:
                            max = 16000
                            
                        for r in range(0,  max):
                            MothOSInts[sequenceIndex+r] = sampleInts[r]
                
                    break
     
    except:
        print("Encoding Step {} ...".format(encodeI))

    
    # mothOS is a byte array, so the index is in bytes
    MothOS = b''.join(struct.pack("<i", i) for i in MothOSInts)
    hash = output[output.find("Validation Hash:") + 17:output.find("Validation Hash:") + 81]
    hashBytes = bytes.fromhex(hash) #convert hash to bytes
    #check if output contains "calculated"
    checksum = ""
   
    if "calculated" in output:
        checksum = output[output.find("calculated") + 11:output.find("calculated") + 13]
    else:
        checksum = output[output.find("Checksum:") + 10:output.find("Checksum:") + 12]
    
    #convert checksum to bytes
    checksumBytes = bytes.fromhex(checksum)
    #replace 33rd last byte with checksum
    MothOS = MothOS[:len(MothOS) - 33] + checksumBytes + MothOS[len(MothOS) - 32:]
    #replace last 32 bytes with hash
    MothOS = MothOS[:len(MothOS) - 32] + hashBytes
     
    with open("MothOS2.ino.bin", "wb") as f:
        f.write(MothOS)

    result = subprocess.run(["python3", "-m", "esptool", "image_info", "MothOS2.ino.bin"], capture_output=True, text=True)
    output = result.stdout
    #print(output)
    


programmerComPorts = []
comPortsStr = ""
#check if comList is empty and exit
if len(comList) == 0:
    print("No COM ports found, please connect MothSynth and try again")
    exit()
    



args = " --port "+com+" --chip esp32s3 --baud 921600  --before default_reset --after hard_reset write_flash -e -z --flash_mode keep --flash_freq keep --flash_size keep 0x0 MothOS.ino.bootloader.bin 0x8000 MothOS.ino.partitions.bin 0xe000 boot_app0.bin 0x10000 MothOS2.ino.bin"

esptool.main(args.split())


