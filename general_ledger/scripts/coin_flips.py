import random

def has_16_in_a_row(flips, count=16):
  """Checks if a list of flips has 16 heads or tails in a row."""
  for i in range(len(flips) - count + 1):
    if len(set(flips[i:i+count])) == 1:  # Check if all elements in the slice are the same
      return True
  return False

num_trials = 100
successes = 0
count=20
events = 1000000
for _ in range(num_trials):
    print(".",end="",flush=True)
    flips = [random.choice(['H', 'T']) for _ in range(events)]
    if has_16_in_a_row(flips,count=count):
        successes += 1
print("\ndone")
probability = successes / num_trials
print(f"Estimated probability: {probability:.4f}")
