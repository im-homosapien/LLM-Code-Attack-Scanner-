import matplotlib.pyplot as plt

# Results from our experiment
labels = ["Without Scanner", "With Scanner"]
asr = [0.241, 0.0]
block_rate = [0.0, 1.0]

# ASR GRAPH
plt.figure()
plt.bar(labels, asr)
plt.title("Attack Success Rate (ASR)")
plt.ylabel("Rate")
plt.ylim(0, 1)
plt.show()

# BLOCK RATE GRAPH
plt.figure()
plt.bar(labels, block_rate)
plt.title("Block Rate")
plt.ylabel("Rate")
plt.ylim(0, 1)
plt.show()