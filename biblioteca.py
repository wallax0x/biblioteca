import json
import csv
import random
import requests
import os
from datetime import datetime
from colorama import init, Fore, Back, Style
import shutil # para restauração

API_KEY = 'dfc1c989'

init(autoreset=True)

arquivo_dados = 'biblioteca.json'
arquivo_log = 'historico.log'
arquivo_senha = 'senha.txt'
diretorio_backups = 'backups_biblioteca'

# GARANTE QUE A PASTA DE BACKUP EXISTE
if not os.path.exists(diretorio_backups):
    try:
        os.makedirs(diretorio_backups)
    except OSError as e:
        print(Fore.RED + f"Erro ao criar diretório de backups '{diretorio_backups}': {e}")
        # Por ora, apenas avisa. As funções de backup/restore verificarão novamente.

# --- FUNCÃO SENHA ---
def criar_senha():
    print(Fore.YELLOW + "Bem-vindo! Como é seu primeiro acesso, por favor crie uma senha.")
    while True:
        senha = input("Digite uma nova senha: ")
        senha_conf = input("Confirme a senha: ")
        if senha == senha_conf and senha.strip() != '':
            with open(arquivo_senha, 'w', encoding='utf-8') as f:
                f.write(senha)
            print(Fore.GREEN + "Senha criada com sucesso!\n")
            return senha
        else:
            print(Fore.RED + "As senhas não coincidem ou são inválidas. Tente novamente.")

def limpar_terminal():
    # PARA WINDOWS
    if os.name == 'nt':
        _ = os.system('cls')
    # PARA MAC E LINUX (os.name é 'posix')
    else:
        _ = os.system('clear')

def pedir_senha():
    if not os.path.exists(arquivo_senha):
        return criar_senha()
    with open(arquivo_senha, 'r', encoding='utf-8') as f:
        senha_cadastrada = f.read().strip()
    for tentativa in range(3):
        senha_digitada = input("Digite sua senha para acessar o sistema: ")
        if senha_digitada == senha_cadastrada:
            print(Fore.GREEN + "Acesso permitido!\n")
            return senha_digitada
        else:
            print(Fore.RED + f"Senha incorreta! Tentativas restantes: {2 - tentativa}")
    print(Fore.RED + "Número máximo de tentativas atingido. Saindo do programa.")
    exit()

def alterar_senha_existente():
    if not os.path.exists(arquivo_senha):
        print(Fore.YELLOW + "Nenhuma senha cadastrada. Crie uma primeiro (normalmente no primeiro acesso).")
        return

    print(Fore.CYAN + "\n--- Alterar Senha ---")
    try:
        with open(arquivo_senha, 'r', encoding='utf-8') as f:
            senha_cadastrada = f.read().strip()
    except IOError:
        print(Fore.RED + "Erro ao ler o arquivo de senha.")
        return

    senha_atual = input("Digite sua senha ATUAL: ")
    if senha_atual != senha_cadastrada:
        print(Fore.RED + "Senha atual incorreta. Alteração cancelada.")
        return

    while True:
        nova_senha = input("Digite a NOVA senha: ")
        if not nova_senha.strip():
            print(Fore.RED + "A nova senha não pode ser vazia.")
            continue
        conf_nova_senha = input("Confirme a NOVA senha: ")
        if nova_senha == conf_nova_senha:
            try:
                with open(arquivo_senha, 'w', encoding='utf-8') as f:
                    f.write(nova_senha)
                registrar_log("Senha alterada pelo usuário.")
                print(Fore.GREEN + "Senha alterada com sucesso!")
            except IOError:
                print(Fore.RED + "Erro ao salvar a nova senha.")
            break
        else:
            print(Fore.RED + "As novas senhas não coincidem. Tente novamente.")

# --- FUNCOES PRINCIPAIS ---
def carregar_dados():
    try:
        with open(arquivo_dados, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(Fore.RED + "Erro ao decodificar o arquivo JSON. Iniciando com biblioteca vazia.")
        return {}

def salvar_dados(dados):
    try:
        with open(arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except IOError:
        print(Fore.RED + "Erro ao salvar os dados da biblioteca.")

def registrar_log(acao):
    try:
        with open(arquivo_log, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {acao}\n")
    except IOError:
        print(Fore.RED + "Erro ao registrar ação no log.")

# --- SISTEMA ---
biblioteca = carregar_dados()

def adicionar_item_com_dados(dados_api, codigo_sugerido=""):
    
    print(Fore.CYAN + "\nPré-cadastrando Filme/Série com dados da internet...")
    codigo_final = codigo_sugerido
    if not codigo_sugerido:
        codigo_final = input("Código único (ex: IMDB id): ").strip()
    else:
        usar_sugestao = input(f"Usar '{codigo_sugerido}' como código? (S/N, Enter para Sim): ").strip().upper()
        if usar_sugestao == 'N':
            codigo_final = input("Digite o código único desejado: ").strip()
    
    if not codigo_final:
        print(Fore.RED + "Código não pode ser vazio.")
        return
    if codigo_final in biblioteca:
        print(Fore.RED + f"O código '{codigo_final}' já existe na biblioteca!")
        return

    titulo = dados_api.get('Title', '')
    print(f"Título: {titulo}")

    tipo_api = dados_api.get('Type', '').capitalize()
    tipo = tipo_api if tipo_api in ["Movie", "Series"] else ""
    tipo_input = input(f"Tipo (Detectado: {tipo_api if tipo_api else 'N/A'}, Filme/Série): ").strip().capitalize()
    if tipo_input: tipo = tipo_input
    elif not tipo: tipo = "Filme" 

    while tipo not in ["Filme", "Série"]:
        print(Fore.RED + "Tipo inválido. Deve ser 'Filme' ou 'Série'.")
        tipo = input("Tipo (Filme/Série): ").strip().capitalize()

    genero_api = dados_api.get('Genre', '')
    genero_input = input(f"Gênero (Detectado: {genero_api}): ").strip()
    genero = genero_input if genero_input else genero_api

    ano_api_str = dados_api.get('Year', '')
    ano_final = ""
    if ano_api_str:
        ano_api_str = ano_api_str.replace('–', '-').split('-')[0].strip() 
        if ano_api_str.isdigit() and len(ano_api_str) == 4:
            ano_final = ano_api_str
    
    ano_input_usuario = input(f"Ano de lançamento (Detectado: {ano_final if ano_final else 'N/A'}, ex: 2022): ").strip()
    if ano_input_usuario: ano_final = ano_input_usuario

    while not (ano_final.isdigit() and len(ano_final) == 4):
        print(Fore.RED + "Ano inválido. Digite um ano com 4 dígitos (ex: 2022).")
        ano_final = input(f"Ano de lançamento (ex: 2022): ").strip()

    status = ""
    while status not in ["Assistido", "Para assistir"]:
        status_input = input("Status (Assistido/Para assistir) [Padrão: Para assistir]: ").strip().capitalize()
        status = "Para assistir" if not status_input else status_input
        if status not in ["Assistido", "Para assistir"]: print(Fore.RED + "Status inválido.")

    nota_imdb_str = dados_api.get('imdbRating', 'N/A')
    sugestao_nota_api = 0.0
    if nota_imdb_str != 'N/A':
        try: sugestao_nota_api = float(nota_imdb_str)
        except ValueError: sugestao_nota_api = 0.0
    
    nota_final = sugestao_nota_api 
    while True:
        try:
            nota_input_str = input(f"Avaliação (0.0-10.0) [IMDb: {nota_imdb_str if nota_imdb_str != 'N/A' else 'N/A'}, Enter para usar IMDb se válido]: ").replace(',', '.')
            if nota_input_str == "": 
                if sugestao_nota_api > 0.0: 
                    nota_final = sugestao_nota_api
                    print(f"Usando nota IMDb: {nota_final}")
                    break
                else: 
                    nota_final = float(input("Avaliação (0.0-10.0) [Obrigatório]: ").replace(',', '.'))
            else: 
                nota_final = float(nota_input_str)

            if 0 <= nota_final <= 10: break
            else: print(Fore.RED + "Nota deve ser entre 0 e 10.")
        except ValueError: print(Fore.RED + "Entrada inválida. Use números (ex: 8.5).")

    favorito_str = input("Favorito? (S/N) [Padrão: N]: ").strip().upper()
    favorito = favorito_str == 'S'
    notas_pessoais = input("Notas pessoais (opcional): ").strip()
    data_adicionado = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # NOVOS CAMPOS
    runtime = dados_api.get('Runtime', 'N/A')
    country = dados_api.get('Country', 'N/A')
    language = dados_api.get('Language', 'N/A')
    poster_url = dados_api.get('Poster', 'N/A')
    awards = dados_api.get('Awards', 'N/A')
    rated_clas = dados_api.get('Rated', 'N/A')


    biblioteca[codigo_final] = {
        'Título': titulo, 'Tipo': tipo, 'Gênero': genero, 'Ano': ano_final,
        'Status': status, 'Avaliação': nota_final, 'Favorito': favorito,
        'Notas': notas_pessoais, 'DataAdicionado': data_adicionado,
        'Runtime': runtime, 'Country': country, 'Language': language, # NOVOS CAMPOS
        'PosterURL': poster_url, 'Awards': awards, 'Rated': rated_clas # NOVOS CAMPOS
    }
    salvar_dados(biblioteca)
    registrar_log(f"Adicionado item (via API): {titulo} ({codigo_final})")
    print(Fore.GREEN + f"\n✅ {titulo} cadastrado com sucesso!")

def buscar_filme_internet(): # Esta função agora é uma das opções do menu de pesquisa online
    titulo_busca = input(Fore.CYAN + "Digite o título do filme/série para buscar detalhes: ")
    url = f"http://www.omdbapi.com/?t={titulo_busca}&apikey={API_KEY}&plot=full&lang=pt" # Usando plot=full
    
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        if dados['Response'] == 'True':
            print(Fore.GREEN + Style.BRIGHT + f"\n--- Detalhes de: {dados['Title']} ---")
            print(f"{Fore.YELLOW}ID IMDb: {dados.get('imdbID')}")
            print(f"{Fore.YELLOW}Título: {dados.get('Title')} ({dados.get('Year')})")
            print(f"{Fore.YELLOW}Tipo: {dados.get('Type')}")
            print(f"{Fore.YELLOW}Classificação: {dados.get('Rated', 'N/A')}")
            print(f"{Fore.YELLOW}Lançamento: {dados.get('Released', 'N/A')}")
            print(f"{Fore.YELLOW}Duração: {dados.get('Runtime', 'N/A')}")
            print(f"{Fore.YELLOW}Gênero: {dados.get('Genre', 'N/A')}")
            print(f"{Fore.YELLOW}Diretor: {dados.get('Director', 'N/A')}")
            print(f"{Fore.YELLOW}Roterista: {dados.get('Writer', 'N/A')}")
            print(f"{Fore.YELLOW}Elenco: {dados.get('Actors', 'N/A')}")
            print(f"{Fore.YELLOW}Idioma: {dados.get('Language', 'N/A')}")
            print(f"{Fore.YELLOW}País: {dados.get('Country', 'N/A')}")
            print(f"{Fore.YELLOW}Prêmios: {dados.get('Awards', 'N/A')}")
            if dados.get('Poster') != 'N/A':
                print(f"{Fore.YELLOW}Link do Pôster: {dados.get('Poster')}")
            
            print(f"\n{Fore.CYAN}--- Sinopse ---")
            print(f"{Style.RESET_ALL}{dados.get('Plot', 'N/A')}")

            print(f"\n{Fore.CYAN}--- Avaliações ---")
            for rating in dados.get('Ratings', []):
                print(f"  {rating['Source']}: {rating['Value']}")
            if not dados.get('Ratings'):
                 print(f"  IMDb Rating: {dados.get('imdbRating', 'N/A')} (Votos: {dados.get('imdbVotes', 'N/A')})")
                 print(f"  Metascore: {dados.get('Metascore', 'N/A')}")


            print(f"\n{Fore.YELLOW}Outras Informações:")
            print(f"  Bilheteria: {dados.get('BoxOffice', 'N/A')}")
            print(f"  Produção: {dados.get('Production', 'N/A')}")
            print(f"  Website: {dados.get('Website', 'N/A') if dados.get('Website') != 'N/A' else 'N/A'}")
            print(Style.RESET_ALL + "-"*50)


            if dados.get('imdbID') not in biblioteca:
                add_choice = input(Fore.BLUE + "\nDeseja adicionar este item à sua biblioteca? (S/N): ").strip().upper()
                if add_choice == 'S':
                    adicionar_item_com_dados(dados, dados.get('imdbID', ''))
            else:
                print(Fore.CYAN + "Este item já está na sua biblioteca.")
        else:
            print(Fore.RED + f"Filme/Série não encontrado: {dados.get('Error', 'Erro desconhecido')}")
    except requests.exceptions.Timeout:
        print(Fore.RED + "Erro na busca: Tempo de requisição esgotado.")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Erro de conexão: {e}")
    except Exception as e:
        print(Fore.RED + f"Erro na busca: {e}")


def adicionar_item():
    print(Fore.CYAN + "\nCadastro de Filme/Série")
    
    codigo = input("Código único (ex: IMDB id): ").strip()
    if not codigo: 
        print(Fore.RED + "Código não pode ser vazio.")
        return
    if codigo in biblioteca:
        print(Fore.RED + "Esse código já existe na biblioteca!")
        return

    titulo = input("Título: ").strip()
    if not titulo:
        print(Fore.RED + "Título não pode ser vazio.")
        return
        
    tipo = ""
    while tipo not in ["Filme", "Série"]:
        tipo = input("Tipo (Filme/Série): ").strip().capitalize()
        if tipo not in ["Filme", "Série"]:
            print(Fore.RED + "Tipo inválido. Digite 'Filme' ou 'Série'.")

    genero = input("Gênero (se múltiplos, separe por vírgula): ").strip()

    # VALIDAÇÃO
    while True:
        ano = input("Ano de lançamento (ex: 2022): ").strip()
        if ano.isdigit() and len(ano) == 4:
            break
        else:
            print(Fore.RED + "Ano inválido. Digite um ano com 4 dígitos (ex: 2022).")

    status = ""
    while status not in ["Assistido", "Para assistir"]:
        status = input("Status (Assistido/Para assistir): ").strip().capitalize()
        if status not in ["Assistido", "Para assistir"]:
            print(Fore.RED + "Status inválido. Digite 'Assistido' ou 'Para assistir'.")

    # VALIDAÇAO DA NOTA
    nota_final_manual = -1.0
    while True:
        try:
            nota_str = input("Avaliação (0.0 a 10.0): ").replace(',', '.')
            nota_final_manual = float(nota_str)
            if 0 <= nota_final_manual <= 10:
                break
            else:
                print(Fore.RED + "Nota deve ser entre 0 e 10.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Use números (ex: 8.5).")

    favorito_str = ""
    while favorito_str not in ["S", "N"]:
        favorito_str = input("Favorito? (S/N): ").strip().upper()
        if favorito_str not in ["S", "N"]:
            print(Fore.RED + "Digite apenas 'S' para sim ou 'N' para não.")

    favorito = favorito_str == 'S'
    notas_pessoais = input("Notas pessoais (opcional): ").strip()
    data_adicionado = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # SALVAR NO DICIONARIO
    # Campos adicionais da API serão 'N/A' por padrão na adição manual
    biblioteca[codigo] = {
        'Título': titulo, 'Tipo': tipo, 'Gênero': genero, 'Ano': ano,
        'Status': status, 'Avaliação': nota_final_manual, 'Favorito': favorito,
        'Notas': notas_pessoais, 'DataAdicionado': data_adicionado,
        'Runtime': 'N/A', 'Country': 'N/A', 'Language': 'N/A',
        'PosterURL': 'N/A', 'Awards': 'N/A', 'Rated': 'N/A'
    }

    salvar_dados(biblioteca)
    registrar_log(f"Adicionado item: {titulo} ({codigo})")
    print(Fore.GREEN + f"\n✅ {titulo} cadastrado com sucesso!")

def listar_itens(filtro=None, valor=None, sort_key=None, reverse_sort=False, items_list_override=None):
    # já com paginação e melhorias
    itens_para_processar = list(items_list_override) if items_list_override is not None else list(biblioteca.items())

    if items_list_override is None and not biblioteca:
        print(Fore.YELLOW + "Biblioteca vazia.")
        return
    
    if filtro and valor:
        valor_lower = valor.lower()
        if filtro == 'Gênero': 
            itens_para_processar = [
                (k, v) for k, v in itens_para_processar 
                if valor_lower in [g.strip().lower() for g in str(v.get(filtro, '')).split(',')]
            ]
        else: 
            itens_para_processar = [(k, v) for k, v in itens_para_processar if str(v.get(filtro, '')).lower() == valor_lower]
    
    if sort_key:
        def get_sort_value(item_tuple):
            item_dict = item_tuple[1]
            value_to_sort = item_dict.get(sort_key)
            if value_to_sort is None:
                return (0 if not reverse_sort else float('inf')) if sort_key in ['Avaliação', 'Ano'] else ("" if not reverse_sort else "\uffff")
            if sort_key == 'Avaliação':
                try: return float(value_to_sort)
                except (ValueError, TypeError): return 0 if not reverse_sort else float('inf')
            if sort_key == 'Ano':
                try: return int(value_to_sort)
                except (ValueError, TypeError): return 0 if not reverse_sort else float('inf')
            return str(value_to_sort).lower() if isinstance(value_to_sort, str) else value_to_sort
        try:
            itens_para_processar.sort(key=get_sort_value, reverse=reverse_sort)
        except TypeError:
            print(Fore.RED + f"Erro ao tentar ordenar por '{sort_key}'. Listando sem ordenação específica.")
    
    if not itens_para_processar:
        if items_list_override is not None or filtro: 
            print(Fore.YELLOW + "Nenhum item encontrado com os critérios especificados.")
        return

    itens_por_pagina = 10 
    pagina_atual = 0
    total_paginas = (len(itens_para_processar) + itens_por_pagina - 1) // itens_por_pagina

    while True:
        limpar_terminal()
        print(Fore.MAGENTA + f"\nItens cadastrados (Página {pagina_atual + 1} de {total_paginas}):")
        
        inicio = pagina_atual * itens_por_pagina
        fim = inicio + itens_por_pagina
        pagina_de_itens = itens_para_processar[inicio:fim]

        for codigo, item in pagina_de_itens:
            avaliacao_item = item.get('Avaliação', 0.0)
            estrelas = '★' * int(round(avaliacao_item / 2)) + '☆' * (5 - int(round(avaliacao_item / 2)))
            fav = Fore.RED + ' ♥' if item.get('Favorito') else ''
            print(Fore.CYAN + "-" * 40)
            print(f"{Fore.YELLOW}Código: {codigo}")
            print(f"Título: {item.get('Título', 'N/A')}{fav}")
            print(f"Tipo: {item.get('Tipo', 'N/A')}")
            print(f"Gênero: {item.get('Gênero', 'N/A')}")
            print(f"Ano: {item.get('Ano', 'N/A')}")
            print(f"Status: {item.get('Status', 'N/A')}")
            print(f"Avaliação: {avaliacao_item} ({estrelas})")
            
            # EXIBIR NOVOS CAMPOS SE EXISTIREM E NÃO FOREM 'N/A'
            if item.get('Runtime') and item.get('Runtime') != 'N/A': print(f"Duração: {item.get('Runtime')}")
            if item.get('Country') and item.get('Country') != 'N/A': print(f"País: {item.get('Country')}")
            if item.get('Language') and item.get('Language') != 'N/A': print(f"Idioma: {item.get('Language')}")
            if item.get('Rated') and item.get('Rated') != 'N/A': print(f"Classificação: {item.get('Rated')}")
            if item.get('Awards') and item.get('Awards') != 'N/A': print(f"Prêmios: {item.get('Awards')[:60] + '...' if len(item.get('Awards')) > 60 else item.get('Awards') }") # Limita prêmios
            if item.get('PosterURL') and item.get('PosterURL') != 'N/A': print(f"Pôster: {item.get('PosterURL')}")
            
            if item.get('Notas'): print(f"Notas Pessoais: {item['Notas']}")
            if item.get('DataAdicionado'): print(f"Adicionado em: {item['DataAdicionado']}")
        print(Fore.CYAN + "-" * 40)

        if total_paginas <= 1:
            break 

        print(f"Página {pagina_atual + 1}/{total_paginas}")
        comando = input(Fore.YELLOW + "P: Próxima, A: Anterior, [Número da Página], S: Sair da listagem: ").strip().lower()

        if comando == 'p':
            if pagina_atual < total_paginas - 1:
                pagina_atual += 1
            else:
                print(Fore.CYAN + "Você já está na última página.")
                input("Pressione Enter para continuar...")
        elif comando == 'a':
            if pagina_atual > 0:
                pagina_atual -= 1
            else:
                print(Fore.CYAN + "Você já está na primeira página.")
                input("Pressione Enter para continuar...")
        elif comando.isdigit() and 1 <= int(comando) <= total_paginas:
            pagina_atual = int(comando) - 1
        elif comando == 's':
            break
        else:
            print(Fore.RED + "Comando inválido.")
            input("Pressione Enter para continuar...")


def estatisticas():
    # OK
    if not biblioteca: 
        print(Fore.YELLOW + "Biblioteca vazia para estatísticas.")
        return
        
    total = len(biblioteca)
    assistidos = sum(1 for i in biblioteca.values() if str(i.get('Status', '')).lower() == 'assistido')
    para_assistir = total - assistidos
    
    soma_avaliacoes = 0
    num_avaliados = 0
    for i in biblioteca.values():
        avaliacao = i.get('Avaliação')
        if avaliacao is not None: 
            try:
                soma_avaliacoes += float(avaliacao)
                num_avaliados += 1
            except ValueError:
                pass 
    media_avaliacao = soma_avaliacoes / num_avaliados if num_avaliados > 0 else 0.0
    
    generos_cont = {}
    for i in biblioteca.values():
        gen_item = i.get('Gênero', '').strip()
        if gen_item: 
            for g_single in gen_item.split(','):
                g_clean = g_single.strip().capitalize()
                if g_clean: generos_cont[g_clean] = generos_cont.get(g_clean, 0) + 1
    
    genero_mais_comum_lista = []
    if generos_cont:
        max_cont = max(generos_cont.values())
        genero_mais_comum_lista = [gen for gen, cont in generos_cont.items() if cont == max_cont]
    
    genero_mais_comum_str = ", ".join(genero_mais_comum_lista) if genero_mais_comum_lista else "Nenhum"

    print(Fore.BLUE + "\n--- Estatísticas da Biblioteca ---")
    print(f"Total de itens: {total}")
    print(f"Assistidos: {assistidos}")
    print(f"Para assistir: {para_assistir}")
    print(f"Média das avaliações (de {num_avaliados} itens avaliados): {media_avaliacao:.2f}")
    print(f"Gênero(s) mais comum(ns): {genero_mais_comum_str}")


def sugerir_por_genero(): # Esta função agora é uma das opções do menu de pesquisa online 😄
    genero_desejado = input("\n🎭 Digite um gênero para sugestão online (ex: Action): ").strip().capitalize()
    if not genero_desejado: 
        print(Fore.YELLOW + "Gênero não pode ser vazio.")
        return

    palavras_chave = ['love', 'war', 'ghost', 'dream', 'life', 'night', 'dark', 'city', 'secret', 'power', 'future', 'magic', 'space', 'time', 'robot', 'dragon', 'king', 'queen', 'world', 'star', 'alien', 'zombie', 'detective', 'mystery', 'adventure', 'journey']
    filmes_encontrados_api = []
    print("\n🔍 Buscando sugestões na internet, aguarde...")
    max_sugestoes = 5

    palavras_busca_prioritaria = [genero_desejado.lower()] + random.sample(palavras_chave, min(len(palavras_chave), 3))

    for palavra_busca in palavras_busca_prioritaria: 
        if len(filmes_encontrados_api) >= max_sugestoes: break
        try:
            resposta_busca = requests.get(f"http://www.omdbapi.com/?s={palavra_busca}&apikey={API_KEY}&type=movie", timeout=7) 
            dados_busca = resposta_busca.json()
            if dados_busca.get('Response') == 'True' and 'Search' in dados_busca:
                for filme_preview in random.sample(dados_busca['Search'], min(len(dados_busca['Search']), 3)): 
                    if len(filmes_encontrados_api) >= max_sugestoes: break
                    imdb_id = filme_preview.get('imdbID')
                    if imdb_id and not any(f.get('imdbID') == imdb_id for f in filmes_encontrados_api):
                        detalhes_resp = requests.get(f"http://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}&plot=short&lang=pt", timeout=7)
                        detalhes = detalhes_resp.json()
                        if detalhes.get('Response') == 'True':
                            generos_filme_api = [g.strip().lower() for g in str(detalhes.get('Genre', '')).split(',')]
                            if genero_desejado.lower() in generos_filme_api:
                                filmes_encontrados_api.append(detalhes)
        except requests.exceptions.Timeout: continue
        except requests.exceptions.RequestException: continue 
        except Exception: continue 

    if filmes_encontrados_api:
        print(f"\n🎞️ Sugestões no gênero '{genero_desejado}' encontradas online (máx {max_sugestoes}):\n")
        for filme_sug in filmes_encontrados_api: 
            print(f"🎬 Título: {filme_sug.get('Title')} ({filme_sug.get('Year')})")
            print(f"⭐ IMDb: {filme_sug.get('imdbRating')}")
            print(f"🎭 Gênero API: {filme_sug.get('Genre')}")
            print(f"📝 Sinopse: {filme_sug.get('Plot')}")
            add_q = input(Fore.BLUE + "Adicionar à biblioteca? (S/N): ").strip().upper()
            if add_q == 'S':
                adicionar_item_com_dados(filme_sug, filme_sug.get('imdbID'))
            print("-" * 50)
    else:
        print(f"\n⚠️ Nenhuma sugestão de filme encontrada online para o gênero '{genero_desejado}'.")


def exportar_csv():
    if not biblioteca: 
        print(Fore.YELLOW + "Biblioteca vazia. Nada para exportar.")
        return
    nome_arquivo = 'biblioteca_exportada.csv'
    try:
        # ADICIONANDO OS NOVOS CAMPOS AO EXPORTAR
        campos = ['Código', 'Título', 'Tipo', 'Gênero', 'Ano', 'Status', 'Avaliação', 'Favorito', 'Notas', 'DataAdicionado',
                  'Runtime', 'Country', 'Language', 'PosterURL', 'Awards', 'Rated']
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=campos, extrasaction='ignore') # extrasaction='ignore' para não dar erro se um item não tiver todos os campos
            writer.writeheader()
            for codigo, item in biblioteca.items():
                # Prepara a linha garantindo que todos os campos existam com .get()
                row_to_write = {campo: item.get(campo, 'N/A') for campo in campos}
                row_to_write['Código'] = codigo # Garante que o código está lá
                row_to_write['Favorito'] = 'Sim' if item.get('Favorito') else 'Não'
                writer.writerow(row_to_write)
        print(Fore.GREEN + f"\nDados exportados com sucesso para '{nome_arquivo}'")
    except IOError:
        print(Fore.RED + f"Erro ao escrever o arquivo CSV '{nome_arquivo}'. Verifique as permissões.")

def importar_csv():
    nome_arquivo = input("Digite o nome do arquivo CSV para importar (ex: biblioteca.csv): ").strip()
    if not os.path.exists(nome_arquivo):
        print(Fore.RED + "Arquivo não encontrado!"); return
    count_imported = 0
    count_skipped = 0
    try:
        with open(nome_arquivo, 'r', encoding='utf-8-sig') as csvfile: 
            reader = csv.DictReader(csvfile)
            if not reader.fieldnames or 'Código' not in reader.fieldnames or 'Título' not in reader.fieldnames:
                print(Fore.RED + "Arquivo CSV inválido ou faltando colunas obrigatórias (Código, Título).")
                return
            for row in reader:
                codigo = str(row.get('Código','')).strip()
                if not codigo: 
                    count_skipped+=1
                    continue
                if codigo in biblioteca: 
                    count_skipped+=1
                    continue
                
                try: avaliacao_csv = float(str(row.get('Avaliação','0.0')).replace(',', '.'))
                except ValueError: avaliacao_csv = 0.0
                if not (0 <= avaliacao_csv <= 10): avaliacao_csv = 0.0

                # ADICIONANDO OS NOVOS CAMPOS AO IMPORTAR (COM VALORES PADRÃO SE AUSENTES)
                biblioteca[codigo] = {
                    'Título': str(row.get('Título','N/A')).strip(),
                    'Tipo': str(row.get('Tipo','Filme')).strip().capitalize(),
                    'Gênero': str(row.get('Gênero','N/A')).strip(),
                    'Ano': str(row.get('Ano','0000')).strip(),
                    'Status': str(row.get('Status','Para assistir')).strip().capitalize(),
                    'Avaliação': avaliacao_csv,
                    'Favorito': str(row.get('Favorito','Não')).strip().lower() == 'sim',
                    'Notas': str(row.get('Notas','')).strip(),
                    'DataAdicionado': str(row.get('DataAdicionado', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),
                    'Runtime': str(row.get('Runtime', 'N/A')).strip(),
                    'Country': str(row.get('Country', 'N/A')).strip(),
                    'Language': str(row.get('Language', 'N/A')).strip(),
                    'PosterURL': str(row.get('PosterURL', 'N/A')).strip(),
                    'Awards': str(row.get('Awards', 'N/A')).strip(),
                    'Rated': str(row.get('Rated', 'N/A')).strip()
                }
                count_imported += 1
        if count_imported > 0: salvar_dados(biblioteca)
        registrar_log(f"Importados {count_imported} itens via CSV. {count_skipped} ignorados.")
        print(Fore.GREEN + f"{count_imported} itens importados com sucesso. {count_skipped} itens ignorados (já existentes ou código inválido).")
    except IOError:
        print(Fore.RED + f"Erro ao ler o arquivo CSV '{nome_arquivo}'.")
    except Exception as e:
        print(Fore.RED + f"Ocorreu um erro inesperado durante a importação: {e}")

def sugestao_aleatoria():
    
    if not biblioteca: 
        print(Fore.YELLOW + "Biblioteca vazia.")
        return
    
    para_assistir = {k:v for k,v in biblioteca.items() if str(v.get('Status','')).lower() == 'para assistir'}
    
    sugestao_escolhida = None
    fonte_sugestao = ""

    if para_assistir:
        favoritos_pa = {k:v for k,v in para_assistir.items() if v.get('Favorito')}
        if favoritos_pa:
            sugestao_escolhida = random.choice(list(favoritos_pa.items()))
            fonte_sugestao = " (Favorito para assistir)"
        else:
            bem_avaliados_pa = {k:v for k,v in para_assistir.items() if v.get('Avaliação', 0.0) >= 7.0}
            if bem_avaliados_pa:
                sugestao_escolhida = random.choice(list(bem_avaliados_pa.items()))
                fonte_sugestao = " (Bem avaliado para assistir)"
            else: 
                sugestao_escolhida = random.choice(list(para_assistir.items()))
                fonte_sugestao = " (Para assistir)"
    else: 
        sugestao_escolhida = random.choice(list(biblioteca.items()))
        fonte_sugestao = " (Aleatório da biblioteca)"
    
    if not sugestao_escolhida: 
        print(Fore.YELLOW + "Não foi possível encontrar uma sugestão.")
        return

    codigo, item = sugestao_escolhida
    print(Fore.CYAN + f"\nSugestão para você{fonte_sugestao}:")
    avaliacao_item = item.get('Avaliação', 0.0)
    estrelas = '★' * int(round(avaliacao_item/2)) + '☆' * (5 - int(round(avaliacao_item/2)))
    fav = Fore.RED + ' ♥' if item.get('Favorito') else ''
    print(f"{Fore.YELLOW}Código: {codigo}")
    print(f"Título: {item.get('Título', 'N/A')}{fav}")
    print(f"Tipo: {item.get('Tipo', 'N/A')}")
    print(f"Gênero: {item.get('Gênero', 'N/A')}")
    print(f"Ano: {item.get('Ano', 'N/A')}")
    print(f"Status: {item.get('Status', 'N/A')}")
    print(f"Avaliação: {avaliacao_item} ({estrelas})")
    if item.get('Notas'): print(f"Notas: {item['Notas']}")
    if item.get('DataAdicionado'): print(f"Adicionado em: {item['DataAdicionado']}")

def buscar_por_titulo(): # Busca na biblioteca local
    termo = input("Digite parte do título para buscar na sua biblioteca: ").lower().strip()
    if not termo: 
        print(Fore.YELLOW + "Termo de busca vazio.")
        return
    
    resultados = [(c,v) for c,v in biblioteca.items() if termo in str(v.get('Título','')).lower()]
    
    if resultados:
        print(Fore.MAGENTA + f"\nEncontrados {len(resultados)} resultados na sua biblioteca:")
        listar_itens(items_list_override=resultados) 
    else:
        print(Fore.YELLOW + "Nenhum resultado encontrado na sua biblioteca.")

def editar_item():
    # os novos campos (Runtime, etc.) não serão editáveis por aqui
    # Eles são preenchidos via API. Se precisar editar, teria que adicionar prompts.
    codigo = input("Digite o código do item a editar: ").strip()
    if codigo not in biblioteca: 
        print(Fore.RED + "Código não encontrado.")
        return
    
    item_original = biblioteca[codigo]
    item_editado = item_original.copy() 

    print(Fore.CYAN + "Editando item. Deixe em branco para manter o valor atual.")
    # (Exibindo os campos extras não editáveis aqui, apenas para informação)
    print(f"{Fore.LIGHTBLACK_EX}Runtime: {item_original.get('Runtime', 'N/A')}, País: {item_original.get('Country', 'N/A')}, Idioma: {item_original.get('Language', 'N/A')}")

    novo_titulo = input(f"Título [{item_original.get('Título')}]: ").strip()
    if novo_titulo: item_editado['Título'] = novo_titulo
    
    novo_tipo = input(f"Tipo [{item_original.get('Tipo')}]: ").strip().capitalize()
    if novo_tipo and novo_tipo in ["Filme", "Série"]: item_editado['Tipo'] = novo_tipo
    elif novo_tipo: print(Fore.YELLOW + "Tipo inválido, mantido o anterior.")

    novo_genero = input(f"Gênero [{item_original.get('Gênero')}]: ").strip()
    if novo_genero: item_editado['Gênero'] = novo_genero

    novo_ano = input(f"Ano [{item_original.get('Ano')}]: ").strip()
    if novo_ano:
        if novo_ano.isdigit() and len(novo_ano) == 4: item_editado['Ano'] = novo_ano
        else: print(Fore.YELLOW + "Ano inválido, mantido o anterior.")
    
    novo_status = input(f"Status [{item_original.get('Status')}]: ").strip().capitalize()
    if novo_status and novo_status in ["Assistido", "Para assistir"]: item_editado['Status'] = novo_status
    elif novo_status: print(Fore.YELLOW + "Status inválido, mantido o anterior.")

    nova_nota_str = input(f"Avaliação [{item_original.get('Avaliação')}]: ").replace(',', '.').strip()
    if nova_nota_str:
        try:
            val = float(nova_nota_str)
            if 0 <= val <= 10: item_editado['Avaliação'] = val
            else: print(Fore.YELLOW + "Nota inválida, mantida a anterior.")
        except ValueError: print(Fore.YELLOW + "Nota inválida (formato), mantida a anterior.")
    
    novo_favorito_str = input(f"Favorito (S/N) [{'S' if item_original.get('Favorito') else 'N'}]: ").strip().upper()
    if novo_favorito_str in ['S','N']: item_editado['Favorito'] = novo_favorito_str == 'S'
    elif novo_favorito_str: print(Fore.YELLOW + "Opção de favorito inválida, mantida a anterior.")

    novas_notas_pessoais = input(f"Notas [{item_original.get('Notas')}]: ").strip()
    if novas_notas_pessoais: item_editado['Notas'] = novas_notas_pessoais
    
    biblioteca[codigo] = item_editado 
    salvar_dados(biblioteca)
    registrar_log(f"Editado item: {codigo} - {item_editado.get('Título')}")
    print(Fore.GREEN + "Item atualizado com sucesso!")

def excluir_item():

    codigo = input("Digite o código do item a excluir: ").strip()
    if codigo in biblioteca:
        confirm = input(Fore.RED + f"Tem certeza que quer excluir '{biblioteca[codigo].get('Título')}'? (S/N): ").strip().upper()
        if confirm == 'S':
            titulo_excluido = biblioteca[codigo].get('Título')
            del biblioteca[codigo]
            salvar_dados(biblioteca)
            registrar_log(f"Excluído item: {codigo} - {titulo_excluido}")
            print(Fore.GREEN + "Item excluído.")
        else:
            print("Exclusão cancelada.")
    else:
        print(Fore.RED + "Código não encontrado.")

# --- NOVAS FUNÇÕES DE UTILITÁRIOS ---
def criar_backup():
    if not os.path.exists(diretorio_backups):
        try:
            os.makedirs(diretorio_backups)
        except OSError as e:
            print(Fore.RED + f"Não foi possível criar o diretório de backups '{diretorio_backups}': {e}")
            return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = os.path.join(diretorio_backups, f"biblioteca_backup_{timestamp}.json")
    try:
        shutil.copy2(arquivo_dados, nome_backup) 
        print(Fore.GREEN + f"Backup criado com sucesso em: {nome_backup}")
        registrar_log(f"Backup da biblioteca criado: {nome_backup}")
    except FileNotFoundError:
        print(Fore.RED + f"Arquivo da biblioteca principal '{arquivo_dados}' não encontrado. Nenhum backup criado.")
    except Exception as e:
        print(Fore.RED + f"Erro ao criar backup: {e}")

def restaurar_backup():
    global biblioteca
    if not os.path.exists(diretorio_backups):
        print(Fore.YELLOW + f"Diretório de backups '{diretorio_backups}' não encontrado. Nenhum backup para restaurar.")
        return

    backups_disponiveis = [f for f in os.listdir(diretorio_backups) if f.startswith("biblioteca_backup_") and f.endswith(".json")]
    if not backups_disponiveis:
        print(Fore.YELLOW + "Nenhum arquivo de backup encontrado.")
        return

    print(Fore.CYAN + "\n--- Restaurar Backup ---")
    print("Backups disponíveis:")
    backups_disponiveis.sort(reverse=True) 
    for i, backup_nome in enumerate(backups_disponiveis):
        print(f"{i + 1}. {backup_nome}")

    try:
        escolha = input("Digite o número do backup para restaurar (ou Enter para cancelar): ").strip()
        if not escolha:
            print("Restauração cancelada.")
            return
        
        idx_escolhido = int(escolha) - 1
        if 0 <= idx_escolhido < len(backups_disponiveis):
            arquivo_backup_escolhido = os.path.join(diretorio_backups, backups_disponiveis[idx_escolhido])
            confirmacao = input(Fore.RED + Style.BRIGHT + 
                                f"ATENÇÃO: Isso substituirá sua biblioteca ATUAL ({arquivo_dados})\n" +
                                f"pelo conteúdo de '{backups_disponiveis[idx_escolhido]}'.\n" +
                                "Essa ação NÃO PODE ser desfeita (a menos que você tenha outro backup).\n" +
                                "Deseja continuar? (S/N): " + Style.RESET_ALL).strip().upper()
            
            if confirmacao == 'S':
                try:
                    shutil.copy2(arquivo_backup_escolhido, arquivo_dados)
                    biblioteca = carregar_dados() 
                    print(Fore.GREEN + f"Biblioteca restaurada com sucesso a partir de '{backups_disponiveis[idx_escolhido]}'.")
                    registrar_log(f"Biblioteca restaurada a partir do backup: {backups_disponiveis[idx_escolhido]}")
                except Exception as e:
                    print(Fore.RED + f"Erro ao restaurar o backup: {e}")
            else:
                print("Restauração cancelada.")
        else:
            print(Fore.RED + "Escolha inválida.")
    except ValueError:
        print(Fore.RED + "Entrada inválida. Por favor, digite um número.")

def normalizar_titulo_para_duplicatas(titulo):
    return " ".join(titulo.lower().split())

def verificar_duplicatas():
    print(Fore.CYAN + "\n--- Verificar Itens Duplicados (Beta) ---")
    if not biblioteca:
        print(Fore.YELLOW + "Biblioteca vazia.")
        return

    possiveis_duplicatas = {}
    for codigo, item in biblioteca.items():
        titulo = item.get('Título', '')
        ano = item.get('Ano', '')
        if not titulo or not ano: 
            continue
        
        chave_duplicata = (normalizar_titulo_para_duplicatas(titulo), ano)
        
        if chave_duplicata not in possiveis_duplicatas:
            possiveis_duplicatas[chave_duplicata] = []
        possiveis_duplicatas[chave_duplicata].append((codigo, titulo))

    duplicatas_encontradas = False
    for (titulo_norm, ano_item), itens_agrupados in possiveis_duplicatas.items():
        if len(itens_agrupados) > 1:
            if not duplicatas_encontradas:
                print(Fore.YELLOW + "Possíveis duplicatas encontradas (mesmo título normalizado e ano):")
            duplicatas_encontradas = True
            print(f"\n{Fore.WHITE}Título: '{titulo_norm}', Ano: {ano_item}")
            for codigo_item, titulo_original in itens_agrupados:
                print(f"  - Código: {Fore.CYAN}{codigo_item}{Fore.WHITE}, Título Original: '{titulo_original}'")
    
    if not duplicatas_encontradas:
        print(Fore.GREEN + "Nenhuma duplicata óbvia encontrada.")
    else:
        print(Fore.YELLOW + "\nRecomendação: Verifique os códigos listados e use a opção 'Editar' ou 'Excluir' para gerenciar.")

def visualizar_historico():
    print(Fore.CYAN + "\n--- Visualizar Histórico de Ações ---")
    try:
        with open(arquivo_log, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        if not linhas:
            print(Fore.YELLOW + "Histórico de ações está vazio.")
            return

        linhas.reverse() 
        
        itens_por_pagina_log = 20
        pagina_atual_log = 0
        total_paginas_log = (len(linhas) + itens_por_pagina_log - 1) // itens_por_pagina_log

        while True:
            limpar_terminal()
            print(Fore.CYAN + f"--- Histórico de Ações (Página {pagina_atual_log + 1}/{total_paginas_log}) ---")
            inicio = pagina_atual_log * itens_por_pagina_log
            fim = inicio + itens_por_pagina_log
            for i, linha in enumerate(linhas[inicio:fim]):
                print(f"{linha.strip()}") 
            
            print("\n" + Fore.YELLOW + "P: Próxima, A: Anterior, [Número da Página], S: Sair")
            cmd = input("Comando: ").lower().strip()

            if cmd == 'p':
                if pagina_atual_log < total_paginas_log - 1: pagina_atual_log += 1
                else: print(Fore.CYAN + "Já está na última página."); input("Enter...")
            elif cmd == 'a':
                if pagina_atual_log > 0: pagina_atual_log -= 1
                else: print(Fore.CYAN + "Já está na primeira página."); input("Enter...")
            elif cmd.isdigit() and 1 <= int(cmd) <= total_paginas_log:
                pagina_atual_log = int(cmd) - 1
            elif cmd == 's': break
            else: print(Fore.RED + "Comando inválido."); input("Enter...")
    except FileNotFoundError:
        print(Fore.YELLOW + "Arquivo de histórico não encontrado.")
    except Exception as e:
        print(Fore.RED + f"Erro ao visualizar histórico: {e}")

def limpar_historico_log():
    print(Fore.CYAN + "\n--- Limpar Histórico de Ações ---")
    confirmacao = input(Fore.RED + Style.BRIGHT + 
                        "ATENÇÃO: Isso apagará TODO o histórico de ações.\n" +
                        "Essa ação NÃO PODE ser desfeita.\n" +
                        "Deseja continuar? (S/N): " + Style.RESET_ALL).strip().upper()
    if confirmacao == 'S':
        try:
            with open(arquivo_log, 'w', encoding='utf-8') as f:
                f.write("") 
            registrar_log("Histórico de ações limpo pelo usuário.") 
            print(Fore.GREEN + "Histórico de ações limpo com sucesso.")
        except IOError:
            print(Fore.RED + "Erro ao tentar limpar o arquivo de histórico.")
    else:
        print("Limpeza do histórico cancelada.")

def menu_utilitarios():
    
    while True:
        limpar_terminal()
        print(Fore.CYAN + Style.BRIGHT + "\n--- Utilitários da Biblioteca ---".center(50, '='))
        print(Fore.YELLOW + "1. Criar Backup da Biblioteca")
        print(Fore.YELLOW + "2. Restaurar Backup da Biblioteca")
        print(Fore.YELLOW + "3. Verificar Itens Duplicados (Beta)")
        print(Fore.YELLOW + "4. Visualizar Histórico de Ações")
        print(Fore.YELLOW + "5. Limpar Histórico de Ações")
        print(Fore.RED + "0. Voltar ao Menu Principal")
        print(Fore.GREEN + "="*50)

        opcao_util = input(Fore.YELLOW + "Escolha uma opção de utilitário: ").strip()
        limpar_terminal()

        if opcao_util == '1': criar_backup()
        elif opcao_util == '2': restaurar_backup()
        elif opcao_util == '3': verificar_duplicatas()
        elif opcao_util == '4': visualizar_historico()
        elif opcao_util == '5': limpar_historico_log()
        elif opcao_util == '0': break
        else: print(Fore.RED + "Opção de utilitário inválida.")
        
        if opcao_util != '0':
            input(Fore.MAGENTA + "\nPressione Enter para continuar...")

# --- NOVAS FUNÇÕES DE PESQUISA ONLINE ---
def _exibir_resultados_busca_ampla(resultados_busca, pagina_atual, total_paginas):
    limpar_terminal()
    print(Fore.MAGENTA + f"\nResultados da Busca Ampla (Página {pagina_atual + 1} de {total_paginas}):")
    for i, res in enumerate(resultados_busca):
        print(f"{Fore.CYAN}{i + 1}. {res.get('Title')} ({res.get('Year')}) - Tipo: {res.get('Type')} [ID: {res.get('imdbID')}]")
    print(Fore.CYAN + "-" * 50)

def buscar_amplo_online():
    termo_busca = input(Fore.CYAN + "Digite o termo para busca ampla online (ex: Batman, Star Wars): ").strip()
    if not termo_busca:
        print(Fore.YELLOW + "Termo de busca não pode ser vazio.")
        return

    print(Fore.BLUE + "Buscando...")
    pagina_api = 1
    resultados_totais_api = []
    total_results_str = "0"

    # Loop para buscar todas as páginas da API OMDb, se houver muitas
    while True:
        url = f"http://www.omdbapi.com/?s={termo_busca}&apikey={API_KEY}&page={pagina_api}"
        try:
            resposta = requests.get(url, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()

            if dados.get('Response') == 'True':
                resultados_totais_api.extend(dados.get('Search', []))
                total_results_str = dados.get('totalResults', "0")
                if len(resultados_totais_api) >= int(total_results_str) or not dados.get('Search'): # Todos os resultados carregados ou não há mais
                    break
                pagina_api += 1
            else:
                if pagina_api == 1: # Se falhou na primeira página
                    print(Fore.RED + f"Nenhum resultado encontrado para '{termo_busca}': {dados.get('Error', '')}")
                break # Sai do loop se não houver mais resultados ou erro
        except requests.exceptions.Timeout:
            print(Fore.RED + "Erro: Tempo de requisição esgotado ao buscar página da API.")
            break
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Erro de conexão com a API: {e}")
            break
        except Exception as e:
            print(Fore.RED + f"Erro inesperado ao buscar na API: {e}")
            break
        if len(resultados_totais_api) > 200 : # Limite para não sobrecarregar
             print(Fore.YELLOW + "Muitos resultados, mostrando os primeiros ~200.")
             break


    if not resultados_totais_api:
        if int(total_results_str) == 0 and pagina_api > 1 : # Chegou ao fim sem erro mas lista vazia (improvável se totalResults > 0)
             pass # A mensagem de "nenhum resultado" já foi dada se falhou na primeira página.
        elif pagina_api == 1 and int(total_results_str) == 0: # Se não houve erro mas a busca não retornou nada.
            print(Fore.YELLOW + f"Nenhum resultado encontrado para '{termo_busca}'.")
        return

    itens_por_pagina_display = 10
    pagina_display_atual = 0
    total_paginas_display = (len(resultados_totais_api) + itens_por_pagina_display - 1) // itens_por_pagina_display

    while True:
        inicio_display = pagina_display_atual * itens_por_pagina_display
        fim_display = inicio_display + itens_por_pagina_display
        pagina_de_resultados = resultados_totais_api[inicio_display:fim_display]
        
        _exibir_resultados_busca_ampla(pagina_de_resultados, pagina_display_atual, total_paginas_display)
        
        if total_paginas_display <= 1 and not pagina_de_resultados: # Caso especial: resultados_totais_api é vazio
             break

        print(f"Total de {len(resultados_totais_api)} resultados encontrados.")
        prompt_escolha = "Escolha um número para ver detalhes, P/A para página, ou S para sair: "
        escolha_usuario = input(Fore.YELLOW + prompt_escolha).strip().lower()

        if escolha_usuario.isdigit():
            idx_escolhido = int(escolha_usuario) - 1
            if 0 <= idx_escolhido < len(pagina_de_resultados):
                imdb_id_selecionado = pagina_de_resultados[idx_escolhido].get('imdbID')
                limpar_terminal()
                print(Fore.BLUE + f"Buscando detalhes para ID: {imdb_id_selecionado}...")
                # Reutiliza buscar_filme_internet, mas passando o ID diretamente
                # Temporariamente, vamos fazer uma chamada direta aqui para detalhes
                url_detalhes = f"http://www.omdbapi.com/?i={imdb_id_selecionado}&apikey={API_KEY}&plot=full&lang=pt"
                try:
                    resp_det = requests.get(url_detalhes, timeout=10)
                    resp_det.raise_for_status()
                    dados_det = resp_det.json()
                    if dados_det.get('Response') == 'True':
                        # Exibe os detalhes de forma similar à buscar_filme_internet
                        print(Fore.GREEN + Style.BRIGHT + f"\n--- Detalhes de: {dados_det['Title']} ---")
                        print(f"{Fore.YELLOW}ID IMDb: {dados_det.get('imdbID')}")
                        # ... (copiar/adaptar exibição de detalhes de buscar_filme_internet) ...
                        print(f"{Fore.YELLOW}Título: {dados_det.get('Title')} ({dados_det.get('Year')})")
                        print(f"{Fore.YELLOW}Tipo: {dados_det.get('Type')}")
                        print(f"{Fore.YELLOW}Gênero: {dados_det.get('Genre', 'N/A')}")
                        print(f"{Fore.YELLOW}Duração: {dados_det.get('Runtime', 'N/A')}")
                        print(f"{Fore.YELLOW}Sinopse: {dados_det.get('Plot', 'N/A')}")
                        print(f"{Fore.YELLOW}Nota IMDb: {dados_det.get('imdbRating', 'N/A')}")
                        print(Style.RESET_ALL + "-"*50)

                        if dados_det.get('imdbID') not in biblioteca:
                             add_q = input(Fore.BLUE + "Adicionar à biblioteca? (S/N): ").strip().upper()
                             if add_q == 'S':
                                 adicionar_item_com_dados(dados_det, dados_det.get('imdbID'))
                        else:
                             print(Fore.CYAN + "Este item já está na sua biblioteca.")

                    else:
                        print(Fore.RED + "Não foi possível obter detalhes para este item.")
                except Exception as e_det:
                    print(Fore.RED + f"Erro ao buscar detalhes: {e_det}")
                input(Fore.MAGENTA + "Pressione Enter para voltar à lista de busca...")


            else:
                print(Fore.RED + "Número inválido.")
                input("Pressione Enter para continuar...")
        elif escolha_usuario == 'p':
            if pagina_display_atual < total_paginas_display - 1: pagina_display_atual += 1
            else: print(Fore.CYAN + "Última página."); input("Enter...")
        elif escolha_usuario == 'a':
            if pagina_display_atual > 0: pagina_display_atual -= 1
            else: print(Fore.CYAN + "Primeira página."); input("Enter...")
        elif escolha_usuario == 's':
            break
        else:
            print(Fore.RED + "Comando inválido.")
            input("Pressione Enter para continuar...")


def detalhes_serie_online():
    titulo_serie = input(Fore.CYAN + "Digite o título da série para ver detalhes de temporadas/episódios: ").strip()
    if not titulo_serie:
        print(Fore.YELLOW + "Título da série não pode ser vazio.")
        return

    url_serie = f"http://www.omdbapi.com/?t={titulo_serie}&apikey={API_KEY}&type=series"
    print(Fore.BLUE + f"Buscando detalhes da série '{titulo_serie}'...")
    try:
        resposta_serie = requests.get(url_serie, timeout=10)
        resposta_serie.raise_for_status()
        dados_serie = resposta_serie.json()

        if dados_serie.get('Response') == 'True':
            total_temporadas_str = dados_serie.get('totalSeasons', '0')
            print(Fore.GREEN + f"\nSérie: {dados_serie.get('Title')} ({dados_serie.get('Year')})")
            print(f"Total de Temporadas: {total_temporadas_str}")

            if int(total_temporadas_str) > 0:
                while True:
                    num_temporada_input = input(Fore.YELLOW + f"Digite o número da temporada (1-{total_temporadas_str}) para ver episódios (ou Enter para sair): ").strip()
                    if not num_temporada_input: break
                    
                    if not num_temporada_input.isdigit() or not (1 <= int(num_temporada_input) <= int(total_temporadas_str)):
                        print(Fore.RED + "Número de temporada inválido.")
                        continue
                    
                    url_temporada = f"http://www.omdbapi.com/?t={titulo_serie}&Season={num_temporada_input}&apikey={API_KEY}"
                    print(Fore.BLUE + f"Buscando episódios da temporada {num_temporada_input}...")
                    try:
                        resp_temp = requests.get(url_temporada, timeout=10)
                        resp_temp.raise_for_status()
                        dados_temp = resp_temp.json()

                        if dados_temp.get('Response') == 'True' and 'Episodes' in dados_temp:
                            print(Fore.CYAN + f"\n--- Episódios da Temporada {dados_temp.get('Season')} ---")
                            for ep in dados_temp.get('Episodes', []):
                                print(f"  Ep.{ep.get('Episode')}: {ep.get('Title')} (Lançamento: {ep.get('Released', 'N/A')}, IMDb: {ep.get('imdbRating', 'N/A')}) ID: {ep.get('imdbID')}")
                            print("-" * 50)
                            # Aqui poderia adicionar opção de ver detalhes de um episódio específico ou adicionar à biblioteca. 🫡
                        else:
                            print(Fore.RED + f"Não foi possível carregar episódios da temporada {num_temporada_input}.")
                    except requests.exceptions.Timeout: print(Fore.RED + "Tempo esgotado ao buscar temporada.")
                    except requests.exceptions.RequestException as e_temp: print(Fore.RED + f"Erro de conexão ao buscar temporada: {e_temp}")
                    except Exception as e_temp_gen: print(Fore.RED + f"Erro ao buscar temporada: {e_temp_gen}")
            else:
                print(Fore.YELLOW + "Não há informações de temporadas para esta série na API.")
            
            if dados_serie.get('imdbID') not in biblioteca:
                 add_q = input(Fore.BLUE + f"\nAdicionar a série '{dados_serie.get('Title')}' à biblioteca? (S/N): ").strip().upper()
                 if add_q == 'S':
                     adicionar_item_com_dados(dados_serie, dados_serie.get('imdbID'))
            else:
                print(Fore.CYAN + "\nEsta série já está na sua biblioteca.")

        else:
            print(Fore.RED + f"Série '{titulo_serie}' não encontrada: {dados_serie.get('Error', 'Erro desconhecido')}")

    except requests.exceptions.Timeout: print(Fore.RED + "Tempo esgotado ao buscar série.")
    except requests.exceptions.RequestException as e_serie: print(Fore.RED + f"Erro de conexão ao buscar série: {e_serie}")
    except Exception as e_serie_gen: print(Fore.RED + f"Erro ao buscar série: {e_serie_gen}")


def menu_pesquisa_online():
    while True:
        limpar_terminal()
        print(Fore.CYAN + Style.BRIGHT + "\n--- Pesquisa e Descoberta Online (OMDb) ---".center(60, '='))
        print(Fore.YELLOW + "1. Buscar detalhes de um filme/série por título exato")
        print(Fore.YELLOW + "2. Sugerir filmes por gênero (busca online)")
        print(Fore.YELLOW + "3. Busca ampla de títulos por termo")
        print(Fore.YELLOW + "4. Ver detalhes de temporadas/episódios de uma série")
        print(Fore.RED + "0. Voltar ao Menu Principal")
        print(Fore.GREEN + "="*60)

        opcao_pesquisa = input(Fore.YELLOW + "Escolha uma opção de pesquisa: ").strip()
        limpar_terminal()

        if opcao_pesquisa == '1': buscar_filme_internet()
        elif opcao_pesquisa == '2': sugerir_por_genero()
        elif opcao_pesquisa == '3': buscar_amplo_online()
        elif opcao_pesquisa == '4': detalhes_serie_online()
        elif opcao_pesquisa == '0': break
        else: print(Fore.RED + "Opção de pesquisa inválida.")
        
        if opcao_pesquisa != '0':
            input(Fore.MAGENTA + "\nPressione Enter para continuar...")


# --- CORES 🫠 ---
def menu():
    print(Fore.GREEN + Style.BRIGHT + "\n" + "="*50)
    print(Fore.CYAN + Style.BRIGHT + " BIBLIOTECA DE FILMES E SÉRIES ".center(50, '='))
    print(Fore.GREEN + "="*50)
    print(Fore.YELLOW + "1 - Adicionar novo filme/série")
    print(Fore.YELLOW + "2 - Listar todos os itens")
    print(Fore.YELLOW + "3 - Listar itens por gênero")
    print(Fore.YELLOW + "4 - Mostrar estatísticas")
    print(Fore.YELLOW + "5 - Exportar dados para CSV")
    print(Fore.YELLOW + "6 - Importar dados de CSV")
    print(Fore.YELLOW + "7 - Buscar por título na biblioteca")
    print(Fore.YELLOW + "8 - Editar um item")
    print(Fore.YELLOW + "9 - Excluir um item")
    print(Fore.YELLOW + "10 - Sugestão aleatória")
    print(Fore.YELLOW + "11 - Pesquisa e Descoberta Online (OMDb)") # OPÇÃO ATUALIZADA
    print(Fore.YELLOW + "12 - Alterar Senha") 
    print(Fore.YELLOW + "13 - Utilitários da Biblioteca") 
    print(Fore.RED + "0 - Sair")
    print(Fore.GREEN + "="*50)

def menu_filtro_genero():
    # Função permanece como está
    if not biblioteca: 
        print(Fore.YELLOW + "Nenhum item na biblioteca para filtrar por gênero.")
        return None
    
    generos_disponiveis = set()
    for item_dict in biblioteca.values():
        gen_item = item_dict.get('Gênero', '').strip()
        if gen_item:
            for g_single in gen_item.split(','): 
                g_clean = g_single.strip().capitalize()
                if g_clean : generos_disponiveis.add(g_clean)
    
    if not generos_disponiveis: 
        print(Fore.YELLOW + "Nenhum gênero encontrado nos itens cadastrados.")
        return None

    generos_list = sorted(list(generos_disponiveis))
    print(Fore.CYAN + "Gêneros disponíveis:")
    for i, g in enumerate(generos_list, 1):
        print(f"{i} - {g}")
    
    while True:
        try:
            escolha_idx_str = input("Escolha um gênero pelo número (ou Enter para cancelar): ")
            if not escolha_idx_str: return None
            idx = int(escolha_idx_str) - 1
            if 0 <= idx < len(generos_list):
                return generos_list[idx]
            else:
                print(Fore.RED + "Opção inválida.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Digite um número.")

# --- PROGRAMA MENU ---
def main():
    limpar_terminal()  
    senha_ok = pedir_senha()  
    if not senha_ok: 
        return 

    while True:  
        menu()  
        opcao = input(Fore.YELLOW + "Escolha uma opção: ").strip()  
        limpar_terminal()

        if opcao == '1': adicionar_item()  
        elif opcao == '2':  
            if not biblioteca: listar_itens()
            else:
                print(Fore.BLUE + "\n--- Opções de Ordenação ---")
                print("1. Padrão (Código)")
                print("2. Título (A-Z)")
                print("3. Título (Z-A)")
                print("4. Ano (Mais Recente)")
                print("5. Ano (Mais Antigo)")
                print("6. Avaliação (Maior)")
                print("7. Avaliação (Menor)")
                print("8. Data de Adição (Mais Recente)")
                print("9. Data de Adição (Mais Antigo)")
                
                sort_choice = input("Escolha a ordenação (ou Enter para padrão): ").strip()
                key_map = {
                    '1': (None, False), '2': ('Título', False), '3': ('Título', True),
                    '4': ('Ano', True), '5': ('Ano', False), '6': ('Avaliação', True),
                    '7': ('Avaliação', False), '8': ('DataAdicionado', True), '9': ('DataAdicionado', False),
                }
                sort_key_to_use, reverse_order = key_map.get(sort_choice, (None, False))
                listar_itens(sort_key=sort_key_to_use, reverse_sort=reverse_order)
        elif opcao == '3':  
            genero_escolhido = menu_filtro_genero()  
            if genero_escolhido:  
                listar_itens(filtro='Gênero', valor=genero_escolhido)  
        elif opcao == '4': estatisticas()  
        elif opcao == '5': exportar_csv()  
        elif opcao == '6': importar_csv()  
        elif opcao == '7': buscar_por_titulo()  
        elif opcao == '8': editar_item()  
        elif opcao == '9': excluir_item()  
        elif opcao == '10': sugestao_aleatoria()  
        elif opcao == '11': menu_pesquisa_online() # CHAMADA ATUALIZADA
        elif opcao == '12': alterar_senha_existente() 
        elif opcao == '13': menu_utilitarios() 
        elif opcao == '0':  
            print(Fore.CYAN + "Obrigado por usar a biblioteca. Até mais!")  
            break  
        else:  
            print(Fore.RED + "Opção inválida. Tente novamente.")  
        
        if opcao != '0':
            input(Fore.MAGENTA + "\nPressione Enter para continuar...")
            limpar_terminal()

if __name__ == "__main__":
    main() 