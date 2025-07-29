"""
Classe principal que lê o arquivo e obtém os dados.
"""

from datetime import datetime, time, date
import io

def obtemCodigoGrandeza(cod):
    codigos = {
        '00': 'Indefinida',
        '01': 'kWh fornecido',
        '02': 'kvarh',
        '03': 'kQh',
        '04': 'V2h',
        '05': 'I2h',
        '06': 'Desativada',
        '07': 'Indefinida',
        '08': 'Vh',
        '09': 'Ih',
        '10': 'kvarhInd Reativo indutivo',
        '11': 'kvarhCap Reativo capacitivo',
        '12': 'kQhInd Qh predominantemente indutivo',
        '13': 'kQhCap Qh predominantemente capacitivo',
        '14': 'kWh recebido',
        '15': 'kvarhInd recebido',
        '16': 'kvarhCap recebido',
        '17': 'Vah',
        '18': 'Vbh',
        '19': 'Vch',
        '20': 'Iah',
        '21': 'Ibh',
        '22': 'Ich',
        '23': 'FPh trifásico direto',
        '24': 'Distorção harmônica total hora',
        '25': 'kVAh trifásico',
        '26': 'FPh reverso',
        '27': 'FPh direto fase A',
        '28': 'FPh direto fase B',
        '29': 'FPh direto fase C',
        '30': 'THDh tensão fase A',
        '31': 'THDh tensão fase B',
        '32': 'THDh tensão fase C',
        '33': 'THDh corrente fase A',
        '34': 'THDh corrente fase B',
        '35': 'THDh corrente fase C',
        '36': 'Vmaxh fase A',
        '37': 'Vmaxh fase B',
        '38': 'Vmaxh fase C',
        '39': 'Vminh fase A',
        '40': 'Vminh fase B',
        '41': 'Vminh fase C',
        '99': 'Canal inexistente'
    }
    return codigos.get(cod, 'Código desconhecido')

class FK7:
    """
    Classe para manipulação de arquivos FK7.
    """
    def __init__(self, arquivo: str):
        """
        Inicializa a instância da classe com o caminho do arquivo FK7.
        :param arquivo: Caminho ou bytes do arquivo FK7.
        """
        
        # Verifica se parâmetro passado é caminho ou bytes
        if isinstance(arquivo, str):
            # É um caminho para arquivo
            self.caminho_arquivo = arquivo
            self.bytes = None
        elif isinstance(arquivo, (bytes, bytearray)):
            # É um conteúdo binário
            self.caminho_arquivo = None
            self.bytes = bytes(arquivo)
        else:
            raise TypeError("A variável 'arquivo' deve ser uma string (caminho) ou bytes.")
        
        # Atributos

        self.parametros = FK7.ClasseParametros()

        self.dado_bruto = None # Dados brutos
        self.hex_blocos = [] # Lista contendo os blocos com dados hexadecimais
        self.qtd_blocos = None # Quantidade de blocos encontrados no arquivo
        self.bloco_presente = {'20':False, '21':False, '22':False, '51':False, '23':False, '24':False, '41':False, '44':False, '42':False, '43':False, '45':False, '46':False, '25':False, '26':False, '27':False, '52':False, '28':False, '80':False, '14':False} # Registra a presença dos tipos diferentes de blocos de leitura
        self.serial_medidor = None # Número do medidor
        self.data_hora_atual = None # Data e hora atual no medidor
        
        # Lê o arquivo assim que a instância da classe é criada
        self.__lerArquivo()

    def __lerArquivo(self):
        """
        Função interna.
        Lê o conteúdo do arquivo FK7 e obtém os atributos.
        """
        try:
            
            if self.caminho_arquivo:
                with open(self.caminho_arquivo, 'rb') as f:
                    dados = f.read()
            elif self.bytes:
                f = io.BytesIO(self.bytes)
                dados = f.read()

            # Dados brutos:
            self.dado_bruto = dados
            
            # Divide os dados em blocos de 256 octetos
            tamanho_bloco = 256
            self.hex_blocos = [[f"{byte:02X}" for byte in dados[i:i + tamanho_bloco]] for i in range(0, len(dados), tamanho_bloco)]
            self.qtd_blocos = len(self.hex_blocos)

            # Cria dicionário com numeração de cada bloco
            self.enum_blocos = []
            for item in self.hex_blocos:
                temp_enum = {i + 1: value for i, value in enumerate(item)}
                self.enum_blocos.append(temp_enum)

            # Identifica os blocos presentes pelo primeiro octeto
            for bloco in self.hex_blocos:
                if bloco[0] in ('20', '21', '22', '51', '23', '24', '41', '44', '42', '43', '45', '46', '25', '26', '27', '52', '28', '80', '14'):
                    self.bloco_presente[bloco[0]] = True

            # Busca o número do medidor:
            self.serial_medidor = self.__obtemSerialMedidor()

            # Encontra data e hora atual no arquivo:
            self.data_hora_atual = self.__obtemDataHora()

            # Gera o nome padrão do arquivo segundo a norma
            self.nome_arquivo = self.__obtemNomeArquivo()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")
        except Exception as e:
            raise IOError(f"Erro ao ler o arquivo: {e}")

    def __obtemSerialMedidor(self):
        """
        Função interna.
        Tenta encontrar o número do medidor através dos blocos lidos.
        """
        serial_encontrado = []

        # Octetos que contém o número do medidor de acordo com a norma NBR 14522
        # Variáveis criadas para facilitar o entendimento
        octeto_inicial = 2
        octeto_final = 5
        
        # Obtém o número do medidor de cada bloco de leitura
        for bloco in self.hex_blocos:
            if bloco[0] in ('20', '21', '22', '51', '23', '24', '41', '44', '42', '43', '45', '46', '26', '27', '52', '28', '80', '14'):
                serial_encontrado.append(int(''.join(bloco[octeto_inicial-1:octeto_final])))
        
        # Verifica se encontrou número de medidor nos blocos e compara se são todos iguais.
        # Se houver diferença entre números de medidores, pode haver algum problema com o arquivo fk7.
        if len(serial_encontrado) > 0:
            if all(item == serial_encontrado[0] for item in serial_encontrado):
                return serial_encontrado[0]
            else:
                raise Exception("Foram encontrados números de medidores distintos no arquivo. Verifique o arquivo.")
        else:
            raise Exception("Não foi encontrado nenhum número de medidor no arquivo.")

    def __obtemDataHora(self):
        """
        Função interna.
        Obtém dados de data e hora.
        """
        data_hora_encontrado = []

        # Octetos que contém a data e a hora de acordo com a norma NBR 14522
        # Variáveis criadas para facilitar o entendimento
        octeto_inicial = 6
        octeto_final = 11

        # Formato da data no arquivo fk7
        formato = "%H%M%S%d%m%y"
        
        # Obtém os dados de data e hora dos blocos de leitura 20, 21, 22 ou 51
        for bloco in self.hex_blocos:
            if bloco[0] in ('20', '21', '22', '51'):
                data_hora_bruto = ''.join(bloco[octeto_inicial-1:octeto_final])
                data_hora_convertido = datetime.strptime(data_hora_bruto, formato)
                data_hora_encontrado.append(data_hora_convertido)
        
        # Verifica se encontrou a data e hora nos blocos e compara se são todos iguais.
        # Se houver diferença entre data e hora dos blocos, pode haver algum problema com o arquivo fk7.
        if len(data_hora_encontrado) > 0:
            if all(item == data_hora_encontrado[0] for item in data_hora_encontrado):
                return data_hora_encontrado[0]
            else:
                #raise Exception("Foram encontrados registros de data e hora distintos no arquivo. Verifique o arquivo.")
                print("Foram encontrados registros de data e hora distintos no arquivo. Verifique o arquivo.")
                return data_hora_encontrado[0]
        else:
            raise Exception("Não foi encontrado nenhum registro de data e hora no arquivo.")

    def __obtemNomeArquivo(self):
        # Extrair os cinco últimos dígitos do número de série do medidor
        nnnnn = str(self.serial_medidor)[-5:]
        
        # Extrair os componentes de data e hora
        segundo = self.data_hora_atual.second
        minuto = self.data_hora_atual.minute
        hora = self.data_hora_atual.hour
        dia = self.data_hora_atual.day
        mes = self.data_hora_atual.month
        
        # Cálculo do total de segundos
        total_segundos = segundo + (minuto * 60) + (hora * 3600) + (dia * 24 * 3600) + (mes * 31 * 24 * 3600)
        
        # Função para converter para base 20
        def para_base_20(numero):
            caracteres_base_20 = "ABCDEFGHIJKLMNOPQRST"
            resultado = ""
            while numero > 0:
                resultado = caracteres_base_20[numero % 20] + resultado
                numero //= 20
            return resultado
        
        # Converter o total de segundos para base 20
        base_20 = para_base_20(total_segundos)
        
        # Obter os 5 primeiros caracteres ou completar com zeros
        base_20 = base_20[-5:].rjust(5, 'A')
        
        # Formar o nome do arquivo
        nome_arquivo = f"{nnnnn}${base_20[0:2]}.{base_20[2:5]}"
        return nome_arquivo

    def lerBloco(self, bloco: dict):

            # Verifica tipo do bloco:
        if bloco[1] in ('20', '21', '22', '51'):
            resultado = self.__lerBlocoLP(bloco)
        elif bloco[1] in ('23','24'):
            resultado = self.__lerBlocoLR(bloco)
        elif bloco[1] in ('41','44'):
            resultado = self.__lerBlocoLR1(bloco)
        elif bloco[1] in ('42','43', '45', '46'):
            resultado = self.__lerBlocoLR23(bloco)
        elif bloco[1] in ('25'):
            resultado = self.__lerBlocoFE(bloco)
        elif bloco[1] in ('26', '27', '52'):
            resultado = self.__lerBlocoCMM(bloco)
        elif bloco[1] in ('28'):
            resultado = self.__lerBlocoRA(bloco)
        elif bloco[1] in ('80'):
            resultado = self.__lerBlocoPM(bloco)
        elif bloco[1] in ('14'):
            resultado = self.__lerBlocoGI(bloco)
        else:
            raise TypeError(f"Tipo de bloco não suportado: {bloco[1]}")

        return resultado

    # Ler parâmetros do bloco tipo LP = Leitura de parâmetros (Leitura de parâmetros - Comando com resposta simples) [Item 3.1.2.1.1 da norma NBR 14522:2008 p16]
    def __lerBlocoLP(self, bloco):
        parametros = FK7.ClasseParametros()
        
        parametros.data_ultimo_intervalo_de_demanda = datetime(year=int(bloco[18]), month=int(bloco[17]), day=int(bloco[16]), hour=int(bloco[13]), minute=int(bloco[14]), second=int(bloco[15]))
        parametros.data_ultima_reposicao_de_demanda = datetime(year=int(bloco[24]), month=int(bloco[23]), day=int(bloco[22]), hour=int(bloco[19]), minute=int(bloco[20]), second=int(bloco[21]))
        parametros.data_penultima_reposicao_de_demanda = datetime(year=int(bloco[30]), month=int(bloco[29]), day=int(bloco[28]), hour=int(bloco[25]), minute=int(bloco[26]), second=int(bloco[27]))
        parametros.hora_inicio_ponta_1 = time(hour=int(bloco[51]), minute=int(bloco[52]))
        parametros.hora_inicio_ponta_2 = time(hour=int(bloco[53]), minute=int(bloco[54]))
        parametros.hora_inicio_ponta_3 = time(hour=int(bloco[55]), minute=int(bloco[56]))
        parametros.hora_inicio_ponta_4 = time(hour=int(bloco[57]), minute=int(bloco[58]))
        parametros.hora_inicio_fora_ponta_1 = time(hour=int(bloco[59]), minute=int(bloco[60]))
        parametros.hora_inicio_fora_ponta_2 = time(hour=int(bloco[61]), minute=int(bloco[62]))
        parametros.hora_inicio_fora_ponta_3 = time(hour=int(bloco[63]), minute=int(bloco[64]))
        parametros.hora_inicio_fora_ponta_4 = time(hour=int(bloco[65]), minute=int(bloco[66]))
        parametros.hora_inicio_horario_reservado_1 = time(hour=int(bloco[67]), minute=int(bloco[68]))
        parametros.hora_inicio_horario_reservado_2 = time(hour=int(bloco[69]), minute=int(bloco[70]))
        parametros.hora_inicio_horario_reservado_3 = time(hour=int(bloco[71]), minute=int(bloco[72]))
        parametros.hora_inicio_horario_reservado_4 = time(hour=int(bloco[73]), minute=int(bloco[74]))
        parametros.numero_de_palavras_leitura_atual = int(bloco[75]+bloco[76]+bloco[77])
        parametros.numero_de_palavras_ultima_reposicao_demanda = int(bloco[78]+bloco[79]+bloco[80])
        parametros.numero_operacoes_reposicao_demanda = int(bloco[81])
        parametros.intervalo_demanda_atual = time(minute=int(bloco[82]))
        parametros.intervalo_demanda_anterior = time(minute=int(bloco[83]))
        
        for i in range(1,16):
            parametros.feriados_nacionais[i] = date(day=int(bloco[84+3*i-3]), month=int(bloco[85+3*i-3]), year=2000+int(bloco[86+3*i-3]))
        
        parametros.numerador_cte_multiplicao_1_canal = int(bloco[129]+bloco[130]+bloco[131])
        parametros.denominador_cte_multiplicao_1_canal = int(bloco[132]+bloco[133]+bloco[134])
        parametros.numerador_cte_multiplicao_2_canal = int(bloco[135]+bloco[136]+bloco[137])
        parametros.denominador_cte_multiplicao_2_canal = int(bloco[138]+bloco[139]+bloco[140])
        parametros.numerador_cte_multiplicao_3_canal = int(bloco[141]+bloco[142]+bloco[143])
        parametros.denominador_cte_multiplicao_3_canal = int(bloco[144]+bloco[145]+bloco[146])
        
        dict_estado_bateria = {'00': 'Bateria boa', '01': 'Bateria com problema'}
        parametros.estado_bateria = dict_estado_bateria.get(bloco[147], 'Código desconhecido')
        
        parametros.versao_software = bloco[148]+bloco[149]
        
        dict_leitura_condicao_horario_reservado = {'00': 'Inativo', '01': 'Ativo'}
        parametros.leitura_condicao_horario_reservado = dict_leitura_condicao_horario_reservado.get(bloco[150], 'Código desconhecido')
        
        dict_forma_calculo_demanda = {'00': 'Tradicional', '01': 'Pesquisada'}
        parametros.forma_calculo_demanda = dict_forma_calculo_demanda.get(bloco[151], 'Código desconhecido')
        
        parametros.modelo_medidor = bloco[153]+bloco[154]
        
        dict_visualizacao_codigos_adicionais_2_canal_visivel = {'00': 'Desativada', '01': 'Ativada'}
        parametros.visualizacao_codigos_adicionais_2_canal_visivel = dict_visualizacao_codigos_adicionais_2_canal_visivel.get(bloco[155], 'Código desconhecido')
        
        dict_condicao_reposicao_demanda_automatica = {'00': 'Desativada', '01': 'Ativada'}
        parametros.condicao_reposicao_demanda_automatica = dict_condicao_reposicao_demanda_automatica.get(bloco[156], 'Código desconhecido')
        
        parametros.dia_reposicao_demanda_automatica = int(bloco[157])

        dict_condicao_horario_verao = {'00': 'Desativado', '01': 'Ativado'}
        parametros.condicao_horario_verao = dict_condicao_horario_verao.get(bloco[158], 'Código desconhecido')

        parametros.dia_fim_horario_inverno = int(bloco[159])
        parametros.mes_fim_horario_inverno = int(bloco[160])
        parametros.dia_fim_horario_verao = int(bloco[161])
        parametros.mes_fim_horario_verao = int(bloco[162])

        # Foi observado que alguns medidores usam padrão invertido do que está na norma NBR 14522, por isso, o trecho a seguir realiza uma verificação simples pra determinar o padrão:
        # Se algum dos horários do conjunto 2 não estiver entre 00 e 23 horas, será considerado o pdrão: {'00': 'Desativado', '01': 'Ativado'}. Caso contrário, será considerado o padrão da norma.
        horas_do_dia = [ '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']

        if all(bloco[i] in horas_do_dia for i in range(172, 195, 2)):
            dict_condicao_conj_2_segmentos_horarios = {'00': 'Ativado', '01': 'Desativado'}
        else:
            dict_condicao_conj_2_segmentos_horarios = {'00': 'Desativado', '01': 'Ativado'}

        parametros.condicao_conj_2_segmentos_horarios = dict_condicao_conj_2_segmentos_horarios.get(bloco[163], 'Código desconhecido')

        parametros.dia_inicio_conjunto_1_seg_horarios_1 = int(bloco[164])
        parametros.mes_inicio_conjunto_1_seg_horarios_1 = int(bloco[165])
        parametros.dia_inicio_conjunto_2_seg_horarios_1 = int(bloco[166])
        parametros.mes_inicio_conjunto_2_seg_horarios_1 = int(bloco[167])
        parametros.dia_inicio_conjunto_1_seg_horarios_2 = int(bloco[168])
        parametros.mes_inicio_conjunto_1_seg_horarios_2 = int(bloco[169])
        parametros.dia_inicio_conjunto_2_seg_horarios_2 = int(bloco[170])
        parametros.mes_inicio_conjunto_2_seg_horarios_2 = int(bloco[171])

        if parametros.condicao_conj_2_segmentos_horarios == 'Ativado':
            parametros.hora_inicio_ponta_conj_2_seg_horarios_1 = time(hour=int(bloco[172]), minute=int(bloco[173]))
            parametros.hora_inicio_ponta_conj_2_seg_horarios_2 = time(hour=int(bloco[174]), minute=int(bloco[175]))
            parametros.hora_inicio_ponta_conj_2_seg_horarios_3 = time(hour=int(bloco[176]), minute=int(bloco[177]))
            parametros.hora_inicio_ponta_conj_2_seg_horarios_4 = time(hour=int(bloco[178]), minute=int(bloco[179]))
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_1 = time(hour=int(bloco[180]), minute=int(bloco[181]))
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_2 = time(hour=int(bloco[182]), minute=int(bloco[183]))
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_3 = time(hour=int(bloco[184]), minute=int(bloco[185]))
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_4 = time(hour=int(bloco[186]), minute=int(bloco[187]))
            parametros.hora_inicio_reservado_conj_2_seg_horarios_1 = time(hour=int(bloco[188]), minute=int(bloco[189]))
            parametros.hora_inicio_reservado_conj_2_seg_horarios_2 = time(hour=int(bloco[190]), minute=int(bloco[191]))
            parametros.hora_inicio_reservado_conj_2_seg_horarios_3 = time(hour=int(bloco[192]), minute=int(bloco[193]))
            parametros.hora_inicio_reservado_conj_2_seg_horarios_4 = time(hour=int(bloco[194]), minute=int(bloco[195]))
        else:
            parametros.hora_inicio_ponta_conj_2_seg_horarios_1 = time(hour=0)
            parametros.hora_inicio_ponta_conj_2_seg_horarios_2 = time(hour=0)
            parametros.hora_inicio_ponta_conj_2_seg_horarios_3 = time(hour=0)
            parametros.hora_inicio_ponta_conj_2_seg_horarios_4 = time(hour=0)
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_1 = time(hour=0)
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_2 = time(hour=0)
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_3 = time(hour=0)
            parametros.hora_inicio_fora_ponta_conj_2_seg_horarios_4 = time(hour=0)
            parametros.hora_inicio_reservado_conj_2_seg_horarios_1 = time(hour=0)
            parametros.hora_inicio_reservado_conj_2_seg_horarios_2 = time(hour=0)
            parametros.hora_inicio_reservado_conj_2_seg_horarios_3 = time(hour=0)
            parametros.hora_inicio_reservado_conj_2_seg_horarios_4 = time(hour=0)
        
        parametros.cod_grandeza_1_canal = obtemCodigoGrandeza(bloco[196])
        parametros.cod_grandeza_2_canal = obtemCodigoGrandeza(bloco[197])
        parametros.cod_grandeza_3_canal = obtemCodigoGrandeza(bloco[198])

        dict_composicao_canais_calculo_fp = {'00':'Tarifa de reativos desativada.', '12':'Canal 1 kWh, canal 2 kvarhInd e kvarhCap', '52':'Canal 1 kWh, canal 2 kvarhInd, canal 3, se houver, kvarhCap', '16': 'Canal 1 kWh, canal 2 kQh'}
        parametros.composicao_calculo_fp = dict_composicao_canais_calculo_fp.get(bloco[199], 'Código desconhecido')

        dict_base_tempo_relogio = {'00':'Indefinida', '01':'Cristal', '02':'Rede CA'}
        parametros.base_tempo_relogio = dict_base_tempo_relogio.get(bloco[200], 'Código desconhecido')

        parametros.tempo_intervalo_memoria_massa = time(minute=int(bloco[204]), second=int(bloco[205]), microsecond=int(bloco[206])*10000) # Multiplica por 10000 para transformar de centésimo para microssegundos

        dict_tipo_reversao_pulsos = {'00':'Indefinido', '01':'Reversão simples', '02':'Reversão dupla'}
        parametros.tipo_reversao_pulsos = dict_tipo_reversao_pulsos.get(bloco[207], 'Código desconhecido')

        dict_segmentos_horarios_sab_dom_fer = { '00': 'Indefinido, vale somente fora ponta', '01': 'Ponta e fora ponta', '02': 'Somente fora ponta', '03': 'Ponta e fora ponta (preferencial em relação ao 01)', '04': 'Fora ponta e reservado', '05': 'Ponta, fora ponta e reservado', '06': 'Fora ponta e reservado (preferencial em relação ao 04)', '07': 'Ponta, fora ponta e reservado (preferencial em relação ao 05)'}
        parametros.seg_horarios_sab = dict_segmentos_horarios_sab_dom_fer.get(bloco[210], 'Código desconhecido')
        parametros.seg_horarios_dom = dict_segmentos_horarios_sab_dom_fer.get(bloco[211], 'Código desconhecido')
        parametros.seg_horarios_fer = dict_segmentos_horarios_sab_dom_fer.get(bloco[212], 'Código desconhecido')

        dict_tipo_tarifa = { '00': 'Azul (horário composto = nenhum)', '01': 'Verde (horário composto = ponta + fora ponta)', '02': 'Irrigante (horário composto = fora ponta + reservado)', '03': 'Amarelo (horário composto = nenhum)', '04': 'Nenhuma'}
        parametros.tipo_tarifa = dict_tipo_tarifa.get(bloco[213], 'Código desconhecido')

        min_intervalo_consumo_reativo = int(bloco[214]+bloco[215])
        if min_intervalo_consumo_reativo >= 60:
            calc_h = min_intervalo_consumo_reativo//60
            calc_min = min_intervalo_consumo_reativo%60
            parametros.intervalo_consumo_reativo = time(hour=calc_h, minute=calc_min)
        else:
            parametros.intervalo_consumo_reativo = time(minute=min_intervalo_consumo_reativo)

        min_intervalo_demanda_reativo = int(bloco[216]+bloco[217])
        if min_intervalo_demanda_reativo >= 60:
            calc_h = min_intervalo_demanda_reativo//60
            calc_min = min_intervalo_demanda_reativo%60
            parametros.intervalo_demanda_reativo = time(hour=calc_h, minute=calc_min)
        else:
            parametros.intervalo_demanda_reativo = time(minute=min_intervalo_demanda_reativo)        
        
        parametros.fp_ref_indutivo = int(bloco[218])
        parametros.fp_ref_capacitivo = int(bloco[219])

        parametros.inicio_horario_reativo_indutivo_1 = time(hour=int(bloco[220]), minute=int(bloco[221]))
        parametros.inicio_horario_reativo_indutivo_2 = time(hour=int(bloco[222]), minute=int(bloco[223]))
        parametros.inicio_horario_reativo_capacitivo_1 = time(hour=int(bloco[224]), minute=int(bloco[225]))
        parametros.inicio_horario_reativo_capacitivo_2 = time(hour=int(bloco[226]), minute=int(bloco[227]))
        
        if parametros.condicao_conj_2_segmentos_horarios == 'Ativado':
            parametros.inicio_horario_reativo_indutivo_conj2_1 = time(hour=int(bloco[228]), minute=int(bloco[229]))
            parametros.inicio_horario_reativo_indutivo_conj2_2 = time(hour=int(bloco[230]), minute=int(bloco[231]))
            parametros.inicio_horario_reativo_capacitivo_conj2_1 = time(hour=int(bloco[232]), minute=int(bloco[233]))
            parametros.inicio_horario_reativo_capacitivo_conj2_2 = time(hour=int(bloco[234]), minute=int(bloco[235]))
        else:
            parametros.inicio_horario_reativo_indutivo_conj2_1 = time(hour=0)
            parametros.inicio_horario_reativo_indutivo_conj2_2 = time(hour=0)
            parametros.inicio_horario_reativo_capacitivo_conj2_1 = time(hour=0)
            parametros.inicio_horario_reativo_capacitivo_conj2_2 = time(hour=0)

        parametros.numero_seg_horarios = int(bloco[238])

        dict_disp_param_medicao = {'00': 'Não disponível', '01': 'Disponível'}
        parametros.disp_param_medicao = dict_disp_param_medicao.get(bloco[240], 'Código desconhecido')

        dict_cond_saida_usuario = {'00': 'Desativada (normal)', '01': 'Ativada (estendida)', '02': 'Mostrador remoto', '04': 'Medidor de 4 quadrantes'}
        parametros.cond_saida_usuario = dict_cond_saida_usuario.get(bloco[241], 'Código desconhecido')

        parametros.upgrade_medidor = int(bloco[242])
        parametros.intervalo_entre_sinc = time(hour=int(bloco[243]))
        parametros.desloc_gmt = int(bloco[244])

        dict_estado_senha = {'00': 'Desativada', '01': 'Ativada'}
        parametros.estado_senha = dict_estado_senha.get(bloco[245], 'Código desconhecido')

        dict_disp_pagina_fiscal = {'00': 'Indisponível', '01': 'Disponível'}
        parametros.disp_pagina_fiscal = dict_disp_pagina_fiscal.get(bloco[246], 'Código desconhecido')

        parametros.num_grupos_canais_disponiveis = int(bloco[247])
        parametros.hora_reposicao_demanda_automatica = int(bloco[249])

        return parametros

    # Ler parâmetros do bloco tipo LR = Leitura de registradores (Leitura de registradores dos canais visíveis – Comando com resposta simples) [Item 3.1.2.1.2 da norma NBR 14522:2008 p21]
    def __lerBlocoLR(self, bloco):
        return None

    # Ler parâmetros do bloco tipo LR1 = Leitura de registradores 1º canal (Leitura de registradores parciais do 1º canal visível – Comando com resposta simples) [Item 3.1.2.1.3 da norma NBR 14522:2008 p26]
    def __lerBlocoLR1(self, bloco):
        return None

    # Ler parâmetros do bloco tipo LR23 = Leitura de registradores 2º e 3° canal (Leitura de registradores parciais dos 2º e 3º canais visíveis – Comando com resposta simples) [Item 3.1.2.1.4 da norma NBR 14522:2008 p30]
    def __lerBlocoLR23(self, bloco):
        return None

    # Ler parâmetros do bloco tipo FE = Falta de energia (Leitura dos períodos de falta de energia – Comando com resposta simples) [Item 3.1.2.1.5 da norma NBR 14522:2008 p34]
    def __lerBlocoFE(self, bloco):
        return None

    # Ler parâmetros do bloco tipo CMM = Contadores da Memória de Massa (Leitura dos contadores da memória de massa – Comando com resposta composta) [Item 3.1.2.1.6 da norma NBR 14522:2008 p35]
    def __lerBlocoCMM(self, bloco):
        return None

    # Ler parâmetros do bloco tipo RA = Registro de alterações (Leitura dos registros de alterações – Comando com resposta simples) [Item 3.1.2.1.7 da norma NBR 14522:2008 p37]
    def __lerBlocoRA(self, bloco):
        return None

    # Ler parâmetros do bloco tipo PM = Parâmetros de medição (Leitura de parâmetros de medição – Comando com resposta simples) [Item 3.1.2.1.8 da norma NBR 14522:2008 p38]
    def __lerBlocoPM(self, bloco):
        return None

    # Ler parâmetros do bloco tipo GI = Grandezas instantâneas (Leitura das grandezas instantâneas – Comando com resposta simples) [Item 3.1.2.1.9 da norma NBR 14522:2008 p42]
    def __lerBlocoGI(self, bloco):
        return None

    class ClasseParametros:
        def __init__(self):
            # Parâmetros de feriados:
            self.feriados_nacionais = {}
