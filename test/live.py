"""
Simple live updating example using magicplot
"""

import magicplot
import time
import numpy
import argparse

from PyQt5 import QtCore

class DummyCCD():
    """Basic dummy camera that provides random frames"""

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.data = numpy.random.normal(0,1,size=(10, self.size_x, self.size_y))
        self.i = 0

    def grab_frame(self):
        self.i += 1
        return self.data[self.i%10]


class DummyShackHartmann():
    """
    Dummy Shack-Hartmann Wavefront Sensor that simulates a grid of spots 
    with random displacements
    """
    def __init__(self, grid_size=10, spot_size=8, jitter=0.5):
        self.grid_size = grid_size  # number of spots in x and y
        self.spot_size = spot_size  # size of each spot in pixels
        self.jitter = jitter  # amount of random displacement
        self.frame_size = grid_size * spot_size
        self.i = 0
        
        # Create base grid of spots
        self.spot_centers = []
        for i in range(grid_size):
            for j in range(grid_size):
                self.spot_centers.append((i * spot_size + spot_size//2, 
                                          j * spot_size + spot_size//2))
        
        # Generate several random displacement patterns to cycle through
        self.num_patterns = 10
        self.displacement_patterns = []
        for _ in range(self.num_patterns):
            displacements = []
            for _ in range(len(self.spot_centers)):
                dx = numpy.random.normal(0, jitter)
                dy = numpy.random.normal(0, jitter)
                displacements.append((dx, dy))
            self.displacement_patterns.append(displacements)
    
    def grab_frame(self):
        # Create a blank frame
        frame = numpy.zeros((self.frame_size, self.frame_size))
        
        # Select the current displacement pattern
        pattern_idx = self.i % self.num_patterns
        displacements = self.displacement_patterns[pattern_idx]
        
        # Draw each spot with its displacement
        for idx, (center_x, center_y) in enumerate(self.spot_centers):
            dx, dy = displacements[idx]
            x = int(center_x + dx)
            y = int(center_y + dy)
            
            # Draw a Gaussian spot
            for i in range(max(0, x-4), min(self.frame_size, x+5)):
                for j in range(max(0, y-4), min(self.frame_size, y+5)):
                    dist = numpy.sqrt((i-x)**2 + (j-y)**2)
                    frame[j, i] += numpy.exp(-0.5 * (dist/1.5)**2)
        
        self.i += 1
        return frame


class DummyPyramidWFS():
    """
    Dummy Pyramid Wavefront Sensor that creates four pupil images 
    with dynamic intensity patterns
    """
    def __init__(self, pupil_size=32, noise_level=0.1):
        self.pupil_size = pupil_size
        self.noise_level = noise_level
        self.frame_size = pupil_size * 2  # Full frame with 4 quadrants
        self.i = 0
        
        # Create base pupil mask (circular aperture)
        self.pupil_mask = numpy.zeros((pupil_size, pupil_size))
        center = pupil_size // 2
        radius = (pupil_size // 2) - 2
        for i in range(pupil_size):
            for j in range(pupil_size):
                if (i - center)**2 + (j - center)**2 <= radius**2:
                    self.pupil_mask[j, i] = 1.0
        
        # Generate base aberration patterns to cycle through
        self.num_patterns = 10
        self.aberration_patterns = []
        for _ in range(self.num_patterns):
            # Create random aberration pattern (simulating wavefront)
            aberration = numpy.random.normal(0, 1, (pupil_size, pupil_size))
            # Apply pupil mask
            aberration = aberration * self.pupil_mask
            self.aberration_patterns.append(aberration)
    
    def grab_frame(self):
        # Select current aberration pattern
        pattern_idx = self.i % self.num_patterns
        aberration = self.aberration_patterns[pattern_idx]
        
        # Create a blank frame for the 4 pupil images
        frame = numpy.zeros((self.frame_size, self.frame_size))
        
        # Calculate intensities for each quadrant based on the aberration
        quad_size = self.pupil_size
        
        # Add the four pupil images with intensity modulations from aberration
        # Top-left quadrant
        frame[:quad_size, :quad_size] = (self.pupil_mask + aberration) * \
                                         numpy.random.normal(1, self.noise_level, 
                                                            (quad_size, quad_size))
        
        # Top-right quadrant
        frame[:quad_size, quad_size:] = (self.pupil_mask - aberration) * \
                                         numpy.random.normal(1, self.noise_level, 
                                                            (quad_size, quad_size))
        
        # Bottom-left quadrant
        frame[quad_size:, :quad_size] = (self.pupil_mask + aberration.T) * \
                                         numpy.random.normal(1, self.noise_level, 
                                                            (quad_size, quad_size))
        
        # Bottom-right quadrant
        frame[quad_size:, quad_size:] = (self.pupil_mask - aberration.T) * \
                                         numpy.random.normal(1, self.noise_level, 
                                                            (quad_size, quad_size))
        
        self.i += 1
        return frame


class DummyPSFCamera():
    """
    Dummy PSF Camera that simulates a point spread function with varying
    aberrations over time
    """
    def __init__(self, size=64, max_strehl=0.9):
        self.size = size
        self.max_strehl = max_strehl
        self.i = 0
        
        # Generate a set of PSF patterns with varying quality
        self.num_patterns = 10
        self.psf_patterns = []
        
        # Create coordinates for PSF calculation
        x = numpy.linspace(-1, 1, size)
        y = numpy.linspace(-1, 1, size)
        self.xx, self.yy = numpy.meshgrid(x, y)
        self.rr = numpy.sqrt(self.xx**2 + self.yy**2)
        
        # Generate different PSFs with varying aberrations
        for i in range(self.num_patterns):
            # Random Zernike coefficients (simplified)
            z_coefs = numpy.random.normal(0, 0.1, 10) * (1 - i/self.num_patterns)
            
            # Calculate PSF (simplified model)
            phase = self.calculate_phase(z_coefs)
            psf = self.phase_to_psf(phase)
            
            # Normalize and add some noise
            psf = psf / psf.max()
            self.psf_patterns.append(psf)
    
    def calculate_phase(self, z_coefs):
        """Simplified Zernike phase calculation"""
        phase = numpy.zeros_like(self.xx)
        
        # Simplified Zernike terms
        # Tip
        phase += z_coefs[0] * self.xx
        # Tilt
        phase += z_coefs[1] * self.yy
        # Defocus
        phase += z_coefs[2] * (2 * self.rr**2 - 1)
        # Astigmatism
        phase += z_coefs[3] * (self.xx**2 - self.yy**2)
        phase += z_coefs[4] * (2 * self.xx * self.yy)
        # Coma
        phase += z_coefs[5] * (3 * self.xx**2 * self.yy - self.yy**3)
        phase += z_coefs[6] * (3 * self.xx * self.yy**2 - self.xx**3)
        # Spherical
        phase += z_coefs[7] * (6 * self.rr**4 - 6 * self.rr**2 + 1)
        
        # Apply aperture
        aperture = self.rr <= 1
        phase = phase * aperture
        
        return phase
    
    def phase_to_psf(self, phase):
        """Convert phase to PSF through simplified FFT"""
        # Create complex amplitude
        complex_amp = numpy.exp(1j * phase) * (self.rr <= 1)
        
        # FFT to get PSF
        psf = numpy.abs(numpy.fft.fftshift(numpy.fft.fft2(complex_amp)))**2
        
        return psf
    
    def grab_frame(self):
        # Get the current PSF pattern
        pattern_idx = self.i % self.num_patterns
        psf = self.psf_patterns[pattern_idx]
        
        # Add some random noise
        psf = psf + numpy.random.normal(0, 0.01, psf.shape)
        psf = numpy.clip(psf, 0, None)  # Ensure non-negative values
        
        self.i += 1
        return psf


class UpdateThread(QtCore.QThread):
    """
    QThread to update plot. Taken from AOplot.
    """
    # Create signals:
    # (a) for updating the plot when new data arrives:
    updateSignal = QtCore.pyqtSignal(object)

    def __init__(self, decimation, sensor_type='ccd', sensor_params=None):
        super(UpdateThread, self).__init__()
        self.decimation = decimation
        self.isRunning = True
        
        # Set up the appropriate sensor based on type
        if sensor_type == 'ccd':
            self.sensor = DummyCCD(100, 100)
        elif sensor_type == 'shwfs':
            if sensor_params is None:
                sensor_params = {'grid_size': 10, 'spot_size': 8, 'jitter': 0.5}
            self.sensor = DummyShackHartmann(**sensor_params)
        elif sensor_type == 'pyramid':
            if sensor_params is None:
                sensor_params = {'pupil_size': 32, 'noise_level': 0.1}
            self.sensor = DummyPyramidWFS(**sensor_params)
        elif sensor_type == 'psf':
            if sensor_params is None:
                sensor_params = {'size': 64, 'max_strehl': 0.9}
            self.sensor = DummyPSFCamera(**sensor_params)
        else:
            # Default to CCD if invalid type specified
            print(f"Warning: Unknown sensor type '{sensor_type}'. Using default CCD.")
            self.sensor = DummyCCD(100, 100)

    # This function is called when you say "updateThread.start()":
    def run(self):
        while self.isRunning:
            frame = self.sensor.grab_frame()
            self.emitUpdateSignal(frame)
            time.sleep(1./self.decimation)

    # This function is called by the RTC everytime new data is ready:
    def emitUpdateSignal(self, data):
        """
        Emit the signal saying that new data is ready, and pass the data to the
        slot that is connected to this signal.

        Args:
            data : ["data", streamname, (data, frame time, frame number)]
                   this is the structure of a data package coming from darc

        Returns:
            nothing
        """
        self.updateSignal.emit(data)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Live data visualization using magicplot")
    parser.add_argument("--sensor", type=str, default="ccd", 
                        choices=["ccd", "shwfs", "pyramid", "psf"],
                        help="Type of sensor to simulate")
    parser.add_argument("--grid-size", type=int, default=10,
                        help="Grid size for Shack-Hartmann WFS")
    parser.add_argument("--pupil-size", type=int, default=32, 
                        help="Pupil size for Pyramid WFS")
    parser.add_argument("--psf-size", type=int, default=64,
                        help="Size of PSF image")
    parser.add_argument("--fps", type=float, default=10,
                        help="Update rate in frames per second")
    args = parser.parse_args()
    
    # Create sensor parameters based on arguments
    sensor_params = None
    if args.sensor == "shwfs":
        sensor_params = {'grid_size': args.grid_size, 'spot_size': 8, 'jitter': 0.5}
    elif args.sensor == "pyramid":
        sensor_params = {'pupil_size': args.pupil_size, 'noise_level': 0.1}
    elif args.sensor == "psf":
        sensor_params = {'size': args.psf_size, 'max_strehl': 0.9}
    
    # Set up the application
    app = magicplot.pyqtgraph.mkQApp()
    plt = magicplot.MagicPlot()
    im = plt.getImageItem()
    plt.show()
    
    # Create and start the update thread
    t = UpdateThread(args.fps, args.sensor, sensor_params)
    t.updateSignal.connect(im.setData)
    t.start()
    
    # Run the application
    app.exec_()
    t.isRunning = False
    t.wait()


if __name__ == "__main__":
    main()


