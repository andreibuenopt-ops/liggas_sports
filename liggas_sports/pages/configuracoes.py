import streamlit as st
from services.services import listar_usuarios, criar_usuario
from utils.style import page_header, divider, section_label

def render():
    page_header("⚙️ Configurações", "Usuários e preferências do sistema")
    perfil = st.session_state.get("usuario", {}).get("perfil","")

    abas = st.tabs(["👤 Usuários", "🔑 Alterar Senha", "ℹ️ Sistema"])

    with abas[0]:
        if perfil != "admin":
            st.warning("Apenas administradores podem gerenciar usuários.")
        else:
            section_label("Usuários Cadastrados")
            usuarios = listar_usuarios()
            for u in usuarios:
                st.markdown(f"""
                <div class="ls-card" style="padding:.6rem 1.2rem">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <span style="font-family:'Barlow Condensed',sans-serif;
                                  font-weight:700;color:#e0e6f0">{u['nome']}</span>
                            <span style="font-family:Rajdhani,sans-serif;color:#405060;
                                  font-size:.85rem;margin-left:10px">{u['email']}</span>
                        </div>
                        <span class="ls-badge ls-badge-{'ativo' if u['ativo'] else 'encerrado'}">{u['perfil'].upper()}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

            divider()
            section_label("Novo Usuário")
            with st.form("form_usuario"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_u = st.text_input("Nome")
                    email_u = st.text_input("E-mail")
                with col2:
                    senha_u = st.text_input("Senha", type="password")
                    perfil_u = st.selectbox("Perfil", ["organizador","arbitro","admin"])
                s = st.form_submit_button("➕ CRIAR USUÁRIO", use_container_width=True, type="primary")
            if s:
                if nome_u and email_u and senha_u:
                    criar_usuario(nome_u, email_u, senha_u, perfil_u)
                    st.success("✅ Usuário criado!")
                else:
                    st.error("Preencha todos os campos.")

    with abas[1]:
        section_label("Alterar Senha")
        with st.form("form_senha"):
            senha_atual = st.text_input("Senha Atual", type="password")
            nova_senha = st.text_input("Nova Senha", type="password")
            confirmar = st.text_input("Confirmar Nova Senha", type="password")
            s = st.form_submit_button("💾 ALTERAR", use_container_width=True, type="primary")
        if s:
            if nova_senha != confirmar:
                st.error("Senhas não coincidem!")
            elif len(nova_senha) < 6:
                st.error("Senha deve ter pelo menos 6 caracteres.")
            else:
                import hashlib
                from database.database import SessionLocal
                from database.models import Usuario
                uid = st.session_state.get("usuario",{}).get("id")
                if uid:
                    db = SessionLocal()
                    u = db.query(Usuario).get(uid)
                    if u and u.senha_hash == hashlib.sha256(senha_atual.encode()).hexdigest():
                        u.senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
                        db.commit(); db.close()
                        st.success("✅ Senha alterada!")
                    else:
                        db.close()
                        st.error("Senha atual incorreta.")

    with abas[2]:
        st.markdown("""
        <div style="background:#0d1a2d;border:1px solid #1e3a5f;border-radius:8px;padding:20px">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.5rem;
                 font-weight:800;color:#00e5ff;letter-spacing:2px">⚡ LiggasSports</div>
            <div style="font-family:Rajdhani,sans-serif;color:#506070;margin-top:8px">
                Plataforma profissional de gerenciamento de campeonatos esportivos
            </div>
            <hr style="border-color:#1a2535;margin:12px 0">
            <div style="font-family:Rajdhani,sans-serif;font-size:.85rem;color:#405060">
                <div>Versão: 3.0</div>
                <div>Stack: Python 3.12 · Streamlit · SQLAlchemy · SQLite/PostgreSQL</div>
                <div>Exports: Excel (OpenPyXL) · PDF (ReportLab) · Charts (Plotly)</div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top:12px;background:#0d1a2d;border:1px solid #1e3a5f;
             border-radius:8px;padding:16px">
            <div class="ls-label">Login Padrão</div>
            <div style="font-family:Rajdhani,sans-serif;color:#c0d0e0">
                Email: <code style="color:#00e5ff">admin@liggassports.com</code><br>
                Senha: <code style="color:#00e5ff">admin123</code>
            </div>
        </div>""", unsafe_allow_html=True)
