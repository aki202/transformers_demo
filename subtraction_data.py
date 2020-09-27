# %%
import random

# %%
def generate_number():
    number = [random.choice(list('012345678')) for _ in range(random.randint(1, 3)) ]
    return int(''.join(number))

# %%
def prepare_data():
    # Prepare data
    input_data = []
    output_data = []

    # Prepare 50,000 data
    while len(input_data) < 50000:
      x = generate_number()
      y = generate_number()
      z = x - y
      input_char = str(x) + '-' + str(y)
      output_char = str(z)

      input_data.append(input_char)
      output_data.append(output_char)

    return input_data, output_data

# %%
if __name__ == '__main__':
      inputs, outputs = prepare_data()
      for input, output in zip(inputs, outputs):
          print('{} {}'.format(input, output))

# %%
