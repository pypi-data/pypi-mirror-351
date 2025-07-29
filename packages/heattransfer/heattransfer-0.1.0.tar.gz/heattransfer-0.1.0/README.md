# HeatTransfer

Pacote Python para cálculo de transferência de calor.

## 📦 Sobre o Projeto

O **HeatTransfer** é um pacote desenvolvido para auxiliar engenheiros, estudantes e profissionais no cálculo de transferência de calor de forma prática e eficiente.

## 👨‍💻 Autor

**Thiago Medeiros**  
Engenheiro de Controle e Automação  
🔗 [GitHub](https://github.com/ThiagoLabM)

## 🚀 Funcionalidades

- Cálculo de condução
- Cálculo de convecção
- Cálculo de radiação
- Outros modelos relacionados à transferência de calor (em desenvolvimento)

## 📥 Instalação

Você pode instalar diretamente via pip:


pip install TransferenciaDeCalor


# Projeto de Transferência de Calor em Tubos Cilíndricos

<img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python Version">
<img src="https://img.shields.io/badge/license-MIT-green" alt="License">

Ferramenta para cálculo preciso de transferência de calor em trocadores de calor cilíndricos concêntricos, com aplicação em sistemas de ar-condicionado e refrigeração industrial.

## 📌 Funcionalidades Principais

- **Cálculo da taxa de transferência de calor** entre fluidos em tubos concêntricos
- **Determinação da LMTD** (Log Mean Temperature Difference)
- **Cálculo de resistências térmicas** individuais (convecção, condução)
- **Suporte a diferentes configurações** de materiais e geometrias

## 📦 Estrutura do Projeto
TransferenciaDeCalor/
├── resistencias/
│ ├── init.py
│ ├── cilindrico2tubos.py # Cálculo de resistências térmicas
│ └── cilindro.py # Cálculos geométricos
├── Calculos.py # Lógica principal
├── setup.py # Configuração do pacote
├── requirements.txt # Dependências
└── examples/ # Exemplos de uso


## 🔧 Instalação

1. Clone o repositório:

git clone https://github.com/seu-usuario/transferencia-calor.git
Instale as dependências:

bash
pip install -r requirements.txt
Instale o pacote:

bash
python setup.py install
🚀 Como Usar
python
from resistencias.cilindrico2tubos import rtotal
from Calculos import taxaTransferenciaCalor

# Exemplo de cálculo
Q = taxaTransferenciaCalor(
    r1=0.1, r2=0.2, 
    h1=10, h2=8, 
    k=50, l=1,
    tqe=100, tfs=30,
    tqs=80, tfe=20
)

print(f"Taxa de transferência: {Q:.2f} W")
📊 Exemplo de Saída
Resistência térmica total: 0.260 K/W
LMTD: 64.93 °C
Taxa de transferência: 248.71 W
📚 Teoria Implementada
Fórmula da Resistência Térmica
math
R_{total} = \frac{1}{h_i A_i} + \frac{\ln(r_o/r_i)}{2πkL} + \frac{1}{h_o A_o}
Cálculo da LMTD
math
\Delta T_{lm} = \frac{(T_{q,ent} - T_{f,sai}) - (T_{q,sai} - T_{f,ent})}{\ln\left(\frac{T_{q,ent} - T_{f,sai}}{T_{q,sai} - T_{f,ent}}\right)}
🤝 Contribuição
Contribuições são bem-vindas! Siga o padrão de código existente e adicione testes para novas funcionalidades.

📄 Licença
MIT License - Consulte o arquivo LICENSE para detalhes.


### Recursos Adicionais Recomendados:

1. **Badges Personalizáveis** (para incluir no topo):
   - Adicione badges do PyPI, testes CI, etc. usando [shields.io](https://shields.io)

2. **Seção de Exemplos Avançados**:
 
   ## 💡 Casos de Uso Avançados
   
   ### Análise de Sensibilidade
 
   # Varie o coeficiente de convecção
   for h in range(5, 15):
       Q = taxaTransferenciaCalor(..., h1=h, ...)
       print(f"Para h={h}: Q={Q:.2f} W")

3. **Documentação de API** (opcional):
 
## 📖 Documentação da API

### `taxaTransferenciaCalor()`
| Parâmetro | Tipo   | Descrição                          |
|-----------|--------|-----------------------------------|
| r1        | float  | Raio interno (m)                  |
| h1        | float  | Coef. convecção interno (W/m²K)   |