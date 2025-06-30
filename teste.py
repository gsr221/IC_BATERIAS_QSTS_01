import time

# Início do tempo
start_time = time.time()

# >>> Aqui vai o seu código principal <<<
time.sleep(61.5)  # Exemplo: simula processamento por 3,5 segundos

# Fim do tempo
end_time = time.time()

# Tempo total em segundos
elapsed_time = end_time - start_time

# Converte para h:m:s
hours, rem = divmod(elapsed_time, 3600)
minutes, seconds = divmod(rem, 60)

# Exibe formatado
print(f"Tempo de execução: {int(hours)}h {int(minutes)}m {seconds:.2f}s")