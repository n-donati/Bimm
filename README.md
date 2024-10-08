# Outer Space Seismic Activity Detection and Data Optimization
Our team's submission for the NASA challenge "Seismic Detection Across the Solar System" proposes a method for detecting significant seismic events on the Moon or Mars and optimizing the data transmitted back to Earth. This optimization minimizes the resources needed for data transmission.

## Pipeline
Our pipeline processes data assumed to be "received" from a Martian module, transforming raw seismic data into a final output of significant seismic events, each denoised and reduced to the most significant sinusoidal waves that construct the original wave. All processes are implemented using Python modules.

Major Processes:
1. Cleaning: The raw data, typically in a comma-separated values file (.csv), is first cleaned to eliminate corrupted or null values using libraries like numpy and pandas.

2. Denoising: We use a DRNN (Dilated Recurrent Neural Network) to denoise the cleaned seismic wave. DRNNs are effective at capturing relevant long-interval dependencies without losing the contextual information of the wave. This step enhances the performance of the subsequent seismic detection algorithm by reducing noise caused by meteorological occurrences, such as strong winds.

3. Detecting: We employ the STA/LTA algorithm to detect significant seismic events. This algorithm monitors continuous changes in the ratio between the average amplitude of short and long time windows. Upon detecting the beginning and end of significant seismic events, the time-interval data samples are extracted for further processing.

4. Summarizing: Iteratively, the relevant seismic event data batches undergo a Fast Fourier Transform (FFT). This transforms each time-amplitude representation into a frequency/amplitude representation, allowing us to select the most significant frequencies that make up the original wave. We determine the proportion of frequencies to keep based on the entropy of the wave, which quantifies the complexity and is normalized to a scale from 0 to 1. These frequencies are then used to reconstruct the final wave to be returned to Earth.

5. Encoding: The processed seismic events are encoded in the miniSEED format, which is standardized for seismic wave analysis and optimized for file size through binary encoding. This is the final output sent back to Earth.

Note: Trials, tests, and individual process developments are conducted in the "playground" directory, which demonstrates the pipeline creation process. The pipeline.py script summarizes the essential blocks needed to process the input and return an output.

Note: From an initial 38,000KB CSV file, a detected seismic event after complete processing has an average size of 16KB.

# Interfaces
This project has two views (or interfaces). The first one is found at path "/simulation/", and the second one at "/home/".

1. Earth Interface: Designed to display a GUI with the results of the pipeline. It features a list of detected events and a window for scientists to select and visualize specific events. The interface also includes three general statistics and basic feedback from ChatGPT, accessible via the "home" template. This is a proposed view for the scientist receiving data from Mars.

2. Martian Module Interface: Shows the pipeline's processes, displaying graphs of raw data, denoised data, and detected seismic events. Aesthetics are primarily reserved for the Earth interface to emphasize clarity and functionality because "Martian module interface" should not exists, as it ideally only requires to be programmed on the martian module.