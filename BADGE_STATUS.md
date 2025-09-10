# 📊 BADGE DE STATUS DE MANUTENÇÃO - Dispositivos

## ✅ Funcionalidade Implementada

### **Objetivo:**
- Badge compacto ao lado do botão "Add Execution"
- Mostra quantidade de manutenções em atraso
- Cores: Verde (OK), Amarelo (próximo), Vermelho (vencido)
- Não clicável, apenas informativo

### **Como Funciona:**

#### **1. Badge Vermelho (Vencido)**
```
[🔴 2] [Add Execution]
```
- **Quando:** Existem manutenções vencidas
- **Número:** Quantidade de itens vencidos
- **Tooltip:** "Itens de manutenção vencidos: 2"
- **Animação:** Pulso sutil para chamar atenção

#### **2. Badge Amarelo (Próximo)**
```
[🟡 1] [Add Execution]
```
- **Quando:** Manutenções vencem em até 7 dias
- **Número:** Quantidade de itens próximos ao vencimento
- **Tooltip:** "Manutenção vence em breve: 1"
- **Cor:** Amarelo com texto preto

#### **3. Badge Verde (OK)**
```
[🟢 OK] [Add Execution]
```
- **Quando:** Todas as manutenções estão em dia
- **Texto:** "OK" 
- **Tooltip:** "Toda manutenção em dia"
- **Cor:** Verde com gradiente

### **Lógica de Prioridade:**
1. **Vermelho** - Tem prioridade máxima (vencido)
2. **Amarelo** - Aparece se não há vencidos mas há próximos
3. **Verde** - Aparece se tudo está OK
4. **Nenhum** - Se não há planos de manutenção

## 🎨 Design Visual

### **Características:**
- ✅ **Compacto:** Pequeno e discreto
- ✅ **Gradiente:** Cores com gradiente para elegância
- ✅ **Sombra:** Efeito de profundidade
- ✅ **Ícones:** Símbolos visuais (⚠️, ⏰, ✅)
- ✅ **Animação:** Pulso sutil para itens vencidos
- ✅ **Tooltip:** Informação adicional no hover

### **Cores:**
```css
Verde:   linear-gradient(135deg, #28a745, #20c997)
Amarelo: linear-gradient(135deg, #ffc107, #e0a800)
Vermelho: linear-gradient(135deg, #dc3545, #c82333)
```

## 🚀 Como Testar

### **1. Cenários de Teste:**

#### **Dispositivo sem Manutenções:**
- Badge não aparece
- Apenas botão "Add Execution"

#### **Dispositivo com Manutenções OK:**
- Badge verde "OK"
- Tooltip: "Toda manutenção em dia"

#### **Dispositivo com Manutenções Próximas:**
- Badge amarelo com número
- Tooltip: "Manutenção vence em breve: X"

#### **Dispositivo com Manutenções Vencidas:**
- Badge vermelho com número
- Tooltip: "Itens de manutenção vencidos: X"
- Animação de pulso

### **2. Instalação:**
```bash
pip install git+https://github.com/diegogodoy06/netbox-maintenance-device.git
docker-compose restart netbox
```

### **3. Verificação:**
1. Acesse qualquer dispositivo
2. Procure o badge ao lado de "Add Execution"
3. Teste tooltip passando mouse sobre o badge
4. Verifique cores conforme status das manutenções

## 📋 Benefícios

### **Para Usuários:**
- ✅ **Visão Rápida:** Status imediato na tela do dispositivo
- ✅ **Priorização:** Cores indicam urgência
- ✅ **Eficiência:** Não precisa abrir aba de manutenção
- ✅ **Informativo:** Tooltip com detalhes

### **Para Gestão:**
- ✅ **Monitoramento:** Identificação rápida de problemas
- ✅ **Planejamento:** Visualização de demanda de manutenção
- ✅ **Compliance:** Garantia de manutenções em dia

**Status: BADGE DE STATUS IMPLEMENTADO! 📊✨**
