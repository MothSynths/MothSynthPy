import subprocess
import struct
import esptool
import random
import os
import sys

# create a list of filenames to load
filenames = [
	"instrument1.raw",
    "instrument2.raw",
    "instrument3.raw",
    "instrument4.raw",
    "instrument5.raw",
    "instrument6.raw",
    "instrument7.raw",
    "instrument8.raw",
    "instrument9.raw",
    "instrument10.raw",
    "instrument11.raw",
    "instrument12.raw"
]

filenamesDrums = [
    "kick1.raw",
    "snare1.raw",
    "special1.raw",
    "hihat1.raw",
    "kick2.raw",
    "snare2.raw",
    "special2.raw",
    "hihat2.raw",
    "kick3.raw",
    "snare3.raw",
    "special3.raw",
    "hihat3.raw"
]

filenamesSfx = [
    "sfx1.raw",
    "sfx2.raw",
    "sfx3.raw",
    "sfx4.raw",
    "sfx5.raw",
    "sfx6.raw",
    "sfx7.raw",
    "sfx8.raw",
    "sfx9.raw",
    "sfx10.raw",
    "sfx11.raw",
    "sfx12.raw"
]

def get_executable_dir():
    """Get the directory where the executable is located."""
    if getattr(sys, 'frozen', False):
        # If the app is frozen by PyInstaller, sys._MEIPASS holds the path to the temp directory
        return os.path.dirname(sys.executable)
    else:
        # If the app is run normally (not packaged), return the current directory
        return os.path.dirname(os.path.abspath(__file__))
    
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
with open(os.path.join(get_executable_dir(),"MothOS.ino.bin"), "rb") as f:
    MothOSCopy = f.read()
    with open(os.path.join(get_executable_dir(),"MothOS2.ino.bin"), "wb") as f2:
        f2.write(MothOSCopy)

#$for loop 0 to 1
tempoIndex = 0
for encodeI in range(0, 3):
    
    # capture output into a variable
    result = subprocess.run(["python3", "-m", "esptool", "image_info", os.path.join(get_executable_dir(),"MothOS2.ino.bin")], capture_output=True, text=True)
    output = result.stdout

    with open(os.path.join(get_executable_dir(),"MothOS2.ino.bin"), "rb") as f:
        MothOS = f.read()
        #convert mothOS into int list
        print("MOTHOS LENGTH {}",len(MothOS))
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
                    with open(os.path.join(get_executable_dir(),"Samples",filename), "rb") as f:
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
                    with open(os.path.join(get_executable_dir(),"Samples",filename), "rb") as f:
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
                    with open(get_executable_dir(),os.path.join("Samples",filename), "rb") as f:
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
     
    with open(os.path.join(get_executable_dir(),"MothOS2.ino.bin"), "wb") as f:
        f.write(MothOS)

    result = subprocess.run(["python3", "-m", "esptool", "image_info", os.path.join(get_executable_dir(),"MothOS2.ino.bin")], capture_output=True, text=True)
    output = result.stdout
    #print(output)
    


programmerComPorts = []
comPortsStr = ""
#check if comList is empty and exit
if len(comList) == 0:
    print("No COM ports found, please connect MothSynth and try again")
    exit()
    



args = " --port "+com+" --chip esp32s3 --baud 921600  --before default_reset --after hard_reset write_flash -e -z --flash_mode keep --flash_freq keep --flash_size keep 0x0 "+os.path.join(get_executable_dir(),"MothOS.ino.bootloader.bin")+" 0x8000 "+os.path.join(get_executable_dir(),"MothOS.ino.partitions.bin")+" 0xe000 "+os.path.join(get_executable_dir(),"boot_app0.bin")+" 0x10000 "+os.path.join(get_executable_dir(),"MothOS2.ino.bin")

esptool.main(args.split())


