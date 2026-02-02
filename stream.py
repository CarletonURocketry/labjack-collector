# type: ignore
# the following script was based on https://github.com/labjack/labjack-ljm-python

from datetime import datetime
import sys
import csv

from labjack import ljm

def streaming():
    
    MAX_REQUESTS = 1000  # The number of eStreamRead calls that will be performed.

    handle = ljm.openS("T7", "USB", "ANY")  # T7, USB connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print(
        "Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i"
        % (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    # Stream Configuration
    aScanListNames = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5", "AIN6", "AIN7", "AIN8", "AIN9", "AIN10", "AIN11", "AIN12", "AIN13"]  # Scan list names to stream, also the headers for CSV
    numAddresses = len(aScanListNames)  # Number of channels we want to read
    aScanList = ljm.namesToAddresses(numAddresses, aScanListNames)[0]
    scanRate = 8000  # Scan rate in Hz (Per channel)
    scansPerRead = 1  # Read Each Channel once per eStreamRead call

    try:
        # Ensure triggered stream is disabled.
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)

        # Enabling internally-clocked stream.
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

        for name in aScanListNames:
            ljm.eWriteName(handle, name + "_RANGE", 1.0) # +/-10 V
            ljm.eWriteName(handle, name + "_NEGATIVE_CH", 199)  # Single-ended
        ljm.eWriteName(handle, "STREAM_RESOLUTION_INDEX", 0)
        ljm.eWriteName(handle, "STREAM_SETTLING_US", 0) # Auto settling time

        # Configure and start stream
        scanRate = ljm.eStreamStart(handle, scansPerRead, numAddresses, aScanList, scanRate)
        print("\nStream started with a scan rate of %0.0f Hz." % scanRate)

        print("\nPerforming %i stream reads." % MAX_REQUESTS)
        start = datetime.now()
        totSkip = 0  # Counter for skipped samples

        i = 1
        with open(f"rate_{scanRate}_scans_{scansPerRead}.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(aScanListNames)

            while i <= MAX_REQUESTS:
                ret = ljm.eStreamRead(handle)
                aData = ret[0]
                scans = len(aData) / numAddresses

                # Write raw data to CSV
                f.write(f"{aData}\n")

                # Count skipped samples (-9999 values)
                # samples occur after a device's stream buffer overflows and are
                # reported after auto-recover mode ends.
                curSkip = aData.count(-9999.0)
                totSkip += curSkip

                print("\neStreamRead %i" % i)

                # Create readable string
                ainStr = ""
                for j in range(numAddresses):
                    ainStr += "%s = %0.5f, " % (aScanListNames[j], aData[j])

                print("  1st scan out of %i: %s" % (scans, ainStr))
                print(
                    "  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = %i"
                    % (curSkip / numAddresses, ret[1], ret[2])
                )

                i += 1
                end = datetime.now()

        print("\nTotal scans = %i" % (i - 1))
        tt = (end - start).seconds + float((end - start).microseconds) / 1_000_000
        print("Time taken = %f seconds" % tt)
        print("LJM Scan Rate = %f scans/second" % scanRate)
        print("Timed Scan Rate = %f scans/second" % ((i - 1) / tt))
        print("Timed Sample Rate = %f samples/second" % ((i - 1) * numAddresses / tt))
        print("Skipped scans = %0.0f" % (totSkip / numAddresses))

    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)

    except Exception:
        e = sys.exc_info()[1]
        print(e)

    try:
        print("\nStop Stream")
        
    except ljm.LJMError:
            ljme = sys.exc_info()[1]
            print(ljme)
    except Exception:
        e = sys.exc_info()[1]
            print(e)
    finally:
            ljm.eStreamStop(handle) 
            # Close Handle
            ljm.close(handle)

    
   

