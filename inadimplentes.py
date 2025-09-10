import streamlit as st
import sqlite3
from datetime import datetime


def get_clientes():
    """Busca todos os clientes do banco de dados"""
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome")
    clientes = c.fetchall()
    conn.close()
    return clientes


def get_inadimplentes():
    """Busca todos os inadimplentes com informações dos clientes"""
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute('''
        SELECT i.id, c.nome, c.telefone, i.status, i.data_atualizacao
        FROM inadimplentes i
        JOIN clientes c ON i.cliente_id = c.id
        ORDER BY i.data_atualizacao DESC
    ''')
    inadimplentes = c.fetchall()
    conn.close()
    return inadimplentes


def cadastrar_inadimplente(cliente_id, status):
    """Cadastra um novo inadimplente"""
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()

    # Verifica se o cliente já está cadastrado como inadimplente
    c.execute("SELECT id FROM inadimplentes WHERE cliente_id = ?", (cliente_id,))
    existe = c.fetchone()

    if existe:
        # Atualiza o status existente
        c.execute('''
            UPDATE inadimplentes 
            SET status = ?, data_atualizacao = DATE('now') 
            WHERE cliente_id = ?
        ''', (status, cliente_id))
        conn.commit()
        conn.close()
        return "atualizado"
    else:
        # Insere novo registro
        c.execute('''
            INSERT INTO inadimplentes (cliente_id, status, data_atualizacao) 
            VALUES (?, ?, DATE('now'))
        ''', (cliente_id, status))
        conn.commit()
        conn.close()
        return "cadastrado"


def remover_inadimplente(inadimplente_id):
    """Remove um inadimplente do banco de dados"""
    conn = sqlite3.connect("barbearia.db")
    c = conn.cursor()
    c.execute("DELETE FROM inadimplentes WHERE id = ?", (inadimplente_id,))
    conn.commit()
    conn.close()


def pagina_inadimplentes():
    st.title("Gestão de Inadimplentes")

    # Sidebar para navegação
    opcao = st.sidebar.selectbox(
        "Escolha uma opção:",
        ["Cadastrar Inadimplente", "Listar Inadimplentes"]
    )

    if opcao == "Cadastrar Inadimplente":
        st.header("Cadastro de Inadimplente")

        # Busca clientes disponíveis
        clientes = get_clientes()

        if not clientes:
            st.warning("Nenhum cliente cadastrado. Cadastre clientes primeiro.")
            return

        # Cria lista de opções para o selectbox
        opcoes_clientes = [
            f"{cliente[1]} - {cliente[2]}" for cliente in clientes]
        cliente_selecionado = st.selectbox(
            "Selecione o Cliente:",
            opcoes_clientes,
            help="Escolha o cliente que será marcado como inadimplente"
        )

        # Status do inadimplente
        status = st.radio(
            "Status:",
            ["Inadimplente", "Regularizado"],
            help="Marque como 'Inadimplente' para clientes em débito ou 'Regularizado' para quem quitou as pendências"
        )

        # Converte status para boolean (True = Inadimplente, False = Regularizado)
        status_bool = True if status == "Inadimplente" else False

        # Botão para cadastrar
        if st.button("Salvar", type="primary"):
            if cliente_selecionado:
                # Pega o ID do cliente selecionado
                indice_cliente = opcoes_clientes.index(cliente_selecionado)
                cliente_id = clientes[indice_cliente][0]

                resultado = cadastrar_inadimplente(cliente_id, status_bool)

                if resultado == "cadastrado":
                    st.success(
                        f"Cliente {clientes[indice_cliente][1]} foi cadastrado como {status.lower()}!")
                elif resultado == "atualizado":
                    st.success(
                        f"Status do cliente {clientes[indice_cliente][1]} foi atualizado para {status.lower()}!")

                st.rerun()

    elif opcao == "Listar Inadimplentes":
        st.header("Lista de Inadimplentes")

        # Busca inadimplentes
        inadimplentes = get_inadimplentes()

        if not inadimplentes:
            st.info("Nenhum inadimplente cadastrado.")
            return

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_status = st.selectbox(
                "Filtrar por Status:",
                ["Todos", "Apenas Inadimplentes", "Apenas Regularizados"]
            )

        # Aplica filtro
        inadimplentes_filtrados = inadimplentes
        if filtro_status == "Apenas Inadimplentes":
            inadimplentes_filtrados = [i for i in inadimplentes if i[3] == 1]
        elif filtro_status == "Apenas Regularizados":
            inadimplentes_filtrados = [i for i in inadimplentes if i[3] == 0]

        # Exibe a lista
        if inadimplentes_filtrados:
            st.subheader(f"Total: {len(inadimplentes_filtrados)} registro(s)")

            for inadimplente in inadimplentes_filtrados:
                id_inadimplente, nome, telefone, status_bool, data_atualizacao = inadimplente
                status_texto = "🔴 Inadimplente" if status_bool else "🟢 Regularizado"

                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.write(f"**{nome}**")
                        st.write(f"📞 {telefone}")

                    with col2:
                        st.write(f"Status: {status_texto}")
                        st.write(f"Atualizado: {data_atualizacao}")

                    with col3:
                        if st.button("❌ Remover", key=f"remove_{id_inadimplente}"):
                            remover_inadimplente(id_inadimplente)
                            st.success(f"Cliente {nome} removido da lista!")
                            st.rerun()

                    st.divider()
        else:
            st.info("Nenhum registro encontrado com os filtros aplicados.")


if __name__ == "__main__":
    main()
