from .resistencias.cilindrico2tubos import rtotal
import math
def deltT(tqe, tfs,tqs,tfe):
    """
    Calcula a diferença de temperatura entre dois pontos.
    
    :param tqe: Temperatura do ponto de entrada do fluido quente.
    :param tfs: Temperatura do ponto de saída do fluido frio.
    :param tqs: Temperatura do ponto de saída do fluido quente.
    :param tfe: Temperatura do ponto de entrada do fluido frio.
    :return: Diferença de temperatura.
    """
    return ((tqe - tfs) - (tqs - tfe))/ math.log((tqe - tfs)/(tqs - tfe))

def taxa_transferencia_calor(r1, r2, h1, h2, k, l, tqe, tfs, tqs, tfe, pi=math.pi):
    """
    Calcula a taxa de transferência de calor entre dois tubos cilíndricos concêntricos.
    
    :param r1: Raio interno do tubo 1.
    :param r2: Raio externo do tubo 2.
    :param k: Condutividade térmica do material do tubo.
    :param l: Comprimento dos tubos.
    :param tqe: Temperatura do ponto de entrada do fluido quente.
    :param tfs: Temperatura do ponto de saída do fluido frio.
    :param tqs: Temperatura do ponto de saída do fluido quente.
    :param tfe: Temperatura do ponto de entrada do fluido frio.
    :return: Taxa de transferência de calor.
    """
    rt = rtotal(r1, r2, h1, h2, k, l, pi)
    dt = deltT(tqe, tfs, tqs, tfe)
    return dt / rt