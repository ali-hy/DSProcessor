import matplotlib.pyplot as plt
import numpy as np

class GraphType:
  Discrete = 0
  Continuous = 1
  BothOnPallete = 2
  Separate = 3

def read_file(path):
  with open('signal1.txt') as file:
    signalType = int(file.readline())
    isPeriodic = int(file.readline())
    nSamples =   int(file.readline())
    t = []
    amp = []
    Wave = None

    if signalType == 0: # zero referes to time domain
      for i in range(nSamples):
        line = file.readline()
        line = line.strip(' ')
        line = line.strip('\n')
        t_i, amp_i = line.split(' ')
        t.append(float(t_i))
        amp.append(float(amp_i))

    elif signalType == 1: # refers to freq domain
      pass

  return t, amp


def graph_wave(t, amp, type=1):
    if type == GraphType.Discrete:
        plt.plot(t, amp, 'ro')

    elif type == GraphType.Continuous:
        plt.plot(t, amp, 'b-')

    elif type == GraphType.BothOnPallete:
        plt.plot(t, amp, 'ro')
        plt.plot(t, amp, 'b-')

    elif type == GraphType.Separate:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        ax1.plot(t, amp, 'ro')
        ax2.plot(t, amp, 'b-')
        plt.tight_layout()

    plt.axvline(x=0, c="red", label="x=0")
    plt.axhline(y=0, c="yellow", label="y=0")
    plt.show()

PI = 3.1415926

def sinusoidal(f, A, theta, t):
   return  A*np.sin(2*PI*t*f + theta)

def cosinusoidal(f, A, theta, t):
   return  A*np.cos(2*PI*t*f + theta)


def generate_wave(wave_type, amplitude, phase_shift, frequency, sampling_frequency, duration = 1):
  LOWER_BOUND = 0
  UPPER_BOUND = duration
  STEP_SIZE = duration/sampling_frequency

  sine =   lambda t : amplitude*np.sin(2*PI*frequency*t + phase_shift)
  cosine = lambda t : amplitude*np.cos(2*PI*frequency*t + phase_shift)

  time_stamps = np.arange(LOWER_BOUND, UPPER_BOUND, STEP_SIZE) #X values
  if wave_type == 1: #sinusoidal
    amps = [sine(t) for t in time_stamps]

  if wave_type == 2: #cosinusoidal
    amps = [cosine(t) for t in time_stamps]



  return time_stamps, amps
