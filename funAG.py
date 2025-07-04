from deap import creator, base, tools, algorithms
import random
from consts import *
from funODSS import DSS
import time as t
import numpy as np

class FunAG:
    def __init__(self):
        self.dss = DSS()
        self.dss.compileFile(linkFile)
        self.barras = self.dss.BusNames()
        self.pmList = []
        creator.create("fitnessMulti", base.Fitness, weights=(-1.0, ))
        #Criando a classe do indivíduo
        creator.create("estrIndiv", list, fitness = creator.fitnessMulti)
        self.fobs = []
    
    
    
    #==Cria um cromossomo (indivíduo) com valores de SOC e barramento aleatórios==#
    def criaCromBatSOC(self):
        soc1=[]
        soc2=[]
        soc3=[]
        bus=[]
        
        #==Cria os valores de SOC aleatórios entre os valores mínimos e máximos==
        for _ in range(len(cc)):
            soc1.append(random.uniform(SOCmin, SOCmax))
            soc2.append(random.uniform(SOCmin, SOCmax))
            soc3.append(random.uniform(SOCmin, SOCmax))

        #==Cria os valores de barramento aleatórios entre 0 e o número de barramentos - 1==#
        bus.append(random.randint(0, len(self.barras)-1))
        
        #==Cria o indivíduo (cromossomo) com os valores de SOC e barramento==#
        #==O indivíduo é uma lista com os valores de SOC1, SOC2, SOC3 e o barramento==#
        #==O tamanho do indivíduo é 3*Tn + 1 (SOCs das fases A, B e C e 1 barramento)==#
        indiv = soc1 + soc2 + soc3 + bus
        
        return indiv
    
    
    def criaCromBatPot(self):
        pot1=[]
        pot2=[]
        pot3=[]
        bus=[]
        
        #==Cria os valores de Pot aleatórios entre os valores de potMax da bateria==#   
        for _ in range(len(cc)):
            pot1.append(random.randint(-self.pmList[0],self.pmList[0]))
            pot2.append(random.randint(-self.pmList[1],self.pmList[1]))
            pot3.append(random.randint(-self.pmList[2],self.pmList[2]))
            
        #==Sorteia o valor de barramento entre 0 e o nº de barramentos - 1===#
        bus.append(random.randint(0, len(self.barras)-1))
        
        indiv = pot1 + pot2 + pot3 + bus
        
        return indiv
    
    #==Método de mutação==#
    def mutateFun(self, indiv):
        novoIndiv = indiv
        novoIndiv = self.criaCromBatSOC()
        return novoIndiv    
    
    
    
    #==Método de cruzamento BLX==#
    def cruzamentoFunBLX(self, indiv1, indiv2):
        newIndiv1 = indiv1
        newIndiv2 = indiv2
        #==Recebe um valor de alfa aleatório==#
        alfa = random.uniform(0.3, 0.5)
        #==Cria um novo indivíduo==#
        for gene in range(len(indiv1)):
            #==Se não for o gene do barramento==#
            if gene != len(indiv1) - 1:
                #==calcula o delta==#
                delta = abs(indiv1[gene] - indiv2[gene])
                #==Calcula o mínimo e o máximo==#
                minGene = min(indiv1[gene], indiv2[gene]) - alfa*delta
                maxGene = max(indiv1[gene], indiv2[gene]) + alfa*delta
                #==Sorteia o novo gene entre o mínimo e o máximo==# 
                newIndiv1[gene] = random.uniform(minGene, maxGene)
                newIndiv2[gene] = random.uniform(minGene, maxGene)
            #==Se for o gene do barramento==#
            else:
                #==calcula o delta==#
                delta = abs(indiv1[gene] - indiv2[gene])
                #==Calcula o mínimo e o máximo==#
                minGene = int(min(indiv1[gene], indiv2[gene]) - alfa*delta)
                maxGene = int(max(indiv1[gene], indiv2[gene]) + alfa*delta)
                #==Sorteia o novo gene entre o mínimo e o máximo==# 
                newIndiv1[gene] = random.randint(minGene, maxGene)
                newIndiv2[gene] = random.randint(minGene, maxGene)
            
        #print(f"newIndiv1: {newIndiv1} - newIndiv2: {newIndiv2}")
        return newIndiv1, newIndiv2    
        
     
        
    def FOBbatSOC(self, indiv):
        n = len(cc)
        
        socA=indiv[:n]
        socB=indiv[n:2*n]
        socC=indiv[2*n:3*n]
        
        #==Verifica se o barramento está dentro dos limites==#
        if indiv[3*n] < 0 or indiv[3*n] >= len(self.barras):
            # print(f"Barramento inválido: {indiv[3*n]}. Deve estar entre 0 e {len(self.barras)-1}.")
            self.fobs.append(1000)
            #print(f"fob: 1000 - Barramento inválido: {indiv[3*n]}. Deve estar entre 0 e {len(self.barras)-1}.")
            return 1000,
        
        barra=str(self.barras[int(indiv[3*n])])
        
        soc = [socA, socB, socC]
        # print(f"Valores de SOC: {soc}")
        

        #==Verifica se os valores de SOC estão dentro dos limites==#
        if any(valSoc < SOCmin or valSoc > SOCmax for fase in soc for valSoc in fase):
            maiorDist = 0
            for fase in soc:
                for valSoc in fase:
                    if valSoc < SOCmin:
                        dist = abs(SOCmin - valSoc)
                        maiorDist = max(maiorDist, dist)
                    elif valSoc > SOCmax:
                        dist = abs(valSoc - SOCmax)
                        maiorDist = max(maiorDist, dist)
            
            self.fobs.append(100 + maiorDist)  # Retorna um valor alto para a FOB 
            #print(f"fob: {100 + maiorDist} - Valores de SOC fora dos limites.")              
            return 100 + maiorDist,  # Retorna um valor alto para a FOB   
        
        #==Calcula a energia máxima de cada fase==#
        #Pmax * dT, onde Pmax é a potência máxima de cada fase e dT é o intervalo de tempo em horas
        deltaE = [[],[],[]]
        E_bat = [self.pmList[0] * dT, self.pmList[1] * dT, self.pmList[2] * dT]
        
        #==Calcula a variação de SOC para cada fase==#
        for fase in range(3):    
            for i in range(n):
                if i == 0:
                    deltaE[fase].append((soc[fase][i]) * E_bat[fase])
                else:
                    deltaE[fase].append((soc[fase][i] - soc[fase][i-1]) * E_bat[fase])
                
        #==Calcula a potência de cada fase==#
        pots = [[],[],[]]
        for fase in range(3):
            for i in range(n):
                if deltaE[fase][i] > 0:
                    pots[fase].append(deltaE[fase][i] / (1 * eficiencia))
                else:
                    pots[fase].append(deltaE[fase][i] / (1 * 1/eficiencia))
            
        deseqs_max = []
        
        #========ALOCA A BATERIA========#        
        for i in range(n):
            potsBat = [pots[0][i], pots[1][i], pots[2][i]]
            # print(f"Potências: {potsBat}")
            # print(f"Barramento: {barra}")
            # print(f"cc: {cc[i]}")
            
            #==Aloca as potências no barramento e os bancos de capacitores e resolve o sistema==#
            self.dss.alocaPot(barramento=barra, listaPoten=potsBat)
            self.dss.solve(cc[i])
        
            #==Recebe as tensões de sequência e as coloca em um dicionário==#
            dfSeqVoltages = self.dss.dfSeqVolt()
            dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
            deseq = dicSecVoltages[' %V2/V1']
            
            deseqs_max.append(max(deseq))
        
        #==Recebe o valor da função objetivo==#
        fobVal = max(deseqs_max)
        
        if fobVal > 2.0:
            #==Se o valor da FOB for maior que 2.0, retorna um valor alto para a FOB==#
            # print('FOB:', fobVal)
            self.fobs.append(10 + fobVal)
            # print(f"fob: {10 + fobVal} - Desequilíbrio máximo maior que 2.0.")
            # print("Indiv:",indiv)
            return 10 + fobVal,
        
        # print('FOB:', fobVal)
        self.fobs.append(fobVal)
        # print(f"fob: {fobVal} - Desequilíbrio máximo dentro dos limites.")
        return fobVal,
        
    
    
    def FOBbatPot(self, indiv):
        n = len(cc)
        
        potA=indiv[:n]
        potB=indiv[n:2*n]
        potC=indiv[2*n:3*n]
        
        #==Verifica se o barramento está dentro dos limites==#
        if indiv[3*n] < 0 or indiv[3*n] >= len(self.barras):
            # print(f"Barramento inválido: {indiv[3*n]}. Deve estar entre 0 e {len(self.barras)-1}.")
            self.fobs.append(1000)
            #print(f"fob: 1000 - Barramento inválido: {indiv[3*n]}. Deve estar entre 0 e {len(self.barras)-1}.")
            return 1000,
        
        barra=str(self.barras[int(indiv[3*n])])
        
        pot = [potA, potB, potC]
        # print(f"Valores de SOC: {soc}")
        
        #==Verifica se os valores de Pot estão dentro dos limites se naão aplica penalidade==#
        if any(abs(valPot) > self.pmList[fase] for fase in range(3) for valPot in pot[fase]):
            dists = [0, 0, 0]
            for fase in range(3):
                for valPot in pot[fase]:
                    if valPot > 1000:
                        dists[fase] = max(dists[fase], abs(valPot-1000))
            
            return 100 + max(dists),
        
        #==Calcula os valores de Energia para poder calcular o SOC==#
        Ebat = max(self.pmList) * dT
        E = np.zeros((3,n))
        
        for fase in range(3):
            for i in range(n):
                if i == 0:
                    E[fase][i] = Ebat*0.8
                else:
                    if pot[fase][i] > 0:
                        E[fase][i] = E[fase][i-1] + pot[fase][i]*dT*eficiencia
                    else:
                        E[fase][i] = E[fase][i-1] + pot[fase][i]*dT*(1/eficiencia)
        
        #==Calcula SOCs a partir dos valores de energia==#
        soc = E * (1/Ebat)
                
        #==Verifica se os valores de SOC estão dentro dos limites se não aplica penalidade==#
        if any(valSoc < SOCmin or valSoc > SOCmax for fase in soc for valSoc in fase):
            maiorDist = 0
            for fase in soc:
                for valSoc in fase:
                    if valSoc < SOCmin:
                        dist = abs(SOCmin - valSoc)
                        maiorDist = max(maiorDist, dist)
                    elif valSoc > SOCmax:
                        dist = abs(valSoc - SOCmax)
                        maiorDist = max(maiorDist, dist)
            
            #print(f"fob: {100 + maiorDist} - Valores de SOC fora dos limites.")              
            return 100 + maiorDist,  # Retorna um valor alto para a FOB
        
        deseqs_max = []
        
        #========SE TUDO ESTIVER DENTRO DOS LIMITES ALOCA A BATERIA========#        
        for i in range(n):
            potsBat = [pot[0][i], pot[1][i], pot[2][i]]
            # print(f"Potências: {potsBat}")
            # print(f"Barramento: {barra}")
            # print(f"cc: {cc[i]}")
            
            #==Aloca as potências no barramento e os bancos de capacitores e resolve o sistema==#
            self.dss.alocaPot(barramento=barra, listaPoten=potsBat)
            self.dss.solve(cc[i])
        
            #==Recebe as tensões de sequência e as coloca em um dicionário==#
            dfSeqVoltages = self.dss.dfSeqVolt()
            dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
            deseq = dicSecVoltages[' %V2/V1']
            
            deseqs_max.append(max(deseq))
        
        #==Recebe o valor da função objetivo==#
        fobVal = max(deseqs_max)
        
        if fobVal > 2.0:
            #==Se o valor da FOB for maior que 2.0, retorna um valor alto para a FOB==#
            # print('FOB:', fobVal)
            self.fobs.append(10 + fobVal)
            # print(f"fob: {10 + fobVal} - Desequilíbrio máximo maior que 2.0.")
            # print("Indiv:",indiv)
            return 10 + fobVal,
        
        # print('FOB:', fobVal)
        self.fobs.append(fobVal)
        # print(f"fob: {fobVal} - Desequilíbrio máximo dentro dos limites.")
        return fobVal,
    
    
    
    ############## Algoritmo Genético ################
    #==Executa o Algoritmo Genético==#
    def execAg(self, pms, probCruz=0.9, probMut=0.1, numGen=700, numRep=1, numPop=200, numTorneio=3, eliteSize=10):
        toolbox = base.Toolbox()
        self.pmList = pms
        t0 = t.time()
        dicMelhoresIndiv = {"cromossomos": [], "fobs": []}
        toolbox.register("mate", self.cruzamentoFunBLX)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.2, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=numTorneio)
        toolbox.register("evaluate", self.FOBbatPot)

        for _ in range(numRep):
            print(f"{converte_tempo(t0)} - Iniciando execução do Algoritmo Genético...")
            
            toolbox.register("indiv", tools.initIterate, creator.estrIndiv, self.criaCromBatPot)
            toolbox.register("pop", tools.initRepeat, list, toolbox.indiv)
            populacao = toolbox.pop(n=numPop)

            hof = tools.HallOfFame(1)
            elite_size = eliteSize

            # Avalia população inicial
            invalid_ind = [ind for ind in populacao if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            best_fobs = []

            for gen in range(numGen):
                # Log da geração
                if gen % 10 == 0:
                    print(f"{converte_tempo(t0)} - Geração {gen + 1} de {numGen}... ")
                    
                # Elitismo
                elite = tools.selBest(populacao, elite_size)

                # Seleção + clone
                offspring = toolbox.select(populacao, len(populacao) - elite_size)
                offspring = list(map(toolbox.clone, offspring))

                # Cruzamento
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < probCruz:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                # Mutação
                for mutant in offspring:
                    if random.random() < probMut:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values

                # Avaliação dos novos
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit

                # Nova população
                populacao[:] = elite + offspring
                hof.update(populacao)

                # Log da geração
                melhor_fob = hof[0].fitness.values[0]
                best_fobs.append(melhor_fob)
                #print(f"Geração {gen + 1}: Melhor FOB = {melhor_fob:.4f}")

            dicMelhoresIndiv["cromossomos"].append(hof[0])
            dicMelhoresIndiv["fobs"].append(hof[0].fitness.values[0])

            return populacao, None, dicMelhoresIndiv, best_fobs, self.barras