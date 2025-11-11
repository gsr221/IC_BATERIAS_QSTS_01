import numpy as np

lista = [
    [0.51233984, 1.22414588, 1.94819592, 2.57120472, 2.65523468, 1.89253208,
     1.50445881, 0.58192758, 1.2958348, 2.06336708, 1.67456388, 2.38773639,
     3.01443276, 2.65515897, 2.18063262, 1.78872302, 1.34951013, 0.70759874,
     0.27765264, 0.53059711, 0.79421281, -0.15976218, -0.61218949, -1.17620422],
    [1.2910754, 1.10363459, 1.54967786, 0.65968702, 1.32577927, 1.52520399,
     1.88528612, 1.94975972, 2.73030702, 3.35142031, 3.44359341, 3.77905658,
     4.59820621, 4.27418639, 3.75447207, 3.11419676, 3.39085986, 2.93774238,
     3.88024219, 4.13989917, 3.26704417, 3.77075225, 4.2082588, 4.24830766],
    [0.28786327, -0.58991002, -0.83804031, -0.31963344, 0.47800506, -0.40102249,
     -0.67018601, -1.60864238, -0.87160436, -0.43170183, -0.65634402, -1.04564004,
     -1.77414879, -1.74787433, -1.51190786, -1.11861972, -1.24704312, -1.79733295,
     -0.86737641, -0.4679906, 0.35831405, -0.54870091, -0.97175755, -0.2770383]
]

arr = np.array(lista)

limite_inferior = 0.2
limite_superior = 0.8

# Máscaras booleanas
mask_acima = arr > limite_superior
mask_abaixo = arr < limite_inferior

if np.any(mask_acima) or np.any(mask_abaixo):
    print('oi')

print("Máscara acima do limite superior:")
print(mask_acima)
print("\nMáscara abaixo do limite inferior:")
print(mask_abaixo)
print('')
# Distâncias
dist_acima = arr[mask_acima] - limite_superior
dist_abaixo = limite_inferior - arr[mask_abaixo]

print("Valores acima do limite:")
print(arr[mask_acima])
print("Distâncias acima:", dist_acima)

print("\nValores abaixo do limite:")
print(arr[mask_abaixo])
print("Distâncias abaixo:", dist_abaixo)