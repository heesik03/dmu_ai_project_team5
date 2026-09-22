import streamlit as st
import ollama
from pypdf import PdfReader
import os

# 페이지 설정
st.set_page_config(page_title="신입사원 문서 교육 및 관리 프로그램", layout="wide")

# 모델 설정 (실습실 환경용 EXAONE 초경량 모델)
MODEL_NAME = "exaone3.5:2.4b"

st.title("🔒 로컬 AI 기반 신입사원 문서 교육 및 관리 프로그램")
st.markdown("외부 유출 걱정 없는 폐쇄망 환경에서 **Ollama(EXAONE)**를 통해 신입사원의 문서 작성과 업무 학습을 지원합니다.")
st.divider()

# --- [사이드바] 관리자 설정 (지침 폴더 & 검색 대상 폴더 설정) ---
st.sidebar.header("📁 1. 관리자 폴더 설정")

# 지침 폴더 경로
st.sidebar.subheader("사내 지침 폴더 경로")
guideline_folder = st.sidebar.text_input("지침 파일들이 있는 폴더 경로:", value="", placeholder="예: C:/Users/USER/Desktop/guidelines")

admin_guideline = ""
if guideline_folder and os.path.exists(guideline_folder) and os.path.isdir(guideline_folder):
    loaded_files_count = 0
    combined_texts = []
    for filename in os.listdir(guideline_folder):
        file_path = os.path.join(guideline_folder, filename)
        if filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_texts.append(f"--- 파일명: {filename} ---\n" + f.read())
                    loaded_files_count += 1
            except:
                pass
        elif filename.endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                pdf_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
                combined_texts.append(f"--- 파일명: {filename} ---\n" + pdf_text)
                loaded_files_count += 1
            except:
                pass
    if loaded_files_count > 0:
        admin_guideline = "\n\n".join(combined_texts)
        st.sidebar.success(f"✅ 총 {loaded_files_count}개의 지침 파일을 불러왔습니다!")

# 지침이 없을 때 기본 규칙 적용
if not admin_guideline:
    admin_guideline = """
    [기본 사내 문서 작성 규칙]
    1. 문서 형식: 보고서는 '제목, 개요, 본문, 결론' 순서로 작성할 것.
    2. 필수 내용: 프로젝트명, 작성자 이름, 작성일자가 반드시 포함되어야 함.
    3. 금지 표현: "~해라", "당장" 등 강압적이거나 비전문적인 어조 사용 금지.
    4. 보안 수칙: 주민등록번호, 연락처 등 개인정보 기재 시 마스킹 처리 필수.
    """
    st.sidebar.info("📌 지침 폴더를 지정하지 않으면 기본 규칙이 적용됩니다.")

st.sidebar.divider()

# 검색용 PC 문서 폴더 경로 (5번 기능용)
st.sidebar.subheader("PC 문서 검색 폴더 경로")
search_folder = st.sidebar.text_input("검색할 사내 문서들이 있는 폴더 경로:", value="", placeholder="예: C:/Users/USER/Desktop/company_docs")


# --- [메인 화면] 기능별 탭 구성 ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✨ 1. 보고서 초안 자동 생성",
    "📝 2. 사내 규칙 문서 점검", 
    "💡 3. 사내·업계 용어 해설", 
    "🛡️ 4. 문서 보안 위험도 판단", 
    "🔍 5. PC 내부 문서 검색"
])

# -------------------------------------------------------------
# 기능 1: 문서 자동 템플릿 생성기 (초안 작성 도우미) [NEW]
# -------------------------------------------------------------
with tab1:
    st.subheader("✨ 사내 맞춤형 보고서 초안 자동 생성")
    st.markdown("작성하고 싶은 보고서의 주제와 핵심 내용만 입력하면, **사내 지침 규칙**에 맞춰 AI가 완벽한 형식의 초안을 작성해 줍니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        doc_project_name = st.text_input("프로젝트명 (또는 문서 제목)", placeholder="예: 차세대 AI 챗봇 도입 건")
        doc_author = st.text_input("작성자 이름 및 직급", placeholder="예: 홍길동 신입사원")
    with col2:
        doc_date = st.text_input("작성일자", placeholder="예: 2026-09-22")
        
    doc_core_content = st.text_area("담고 싶은 핵심 내용이나 아이디어:", height=150, placeholder="예: 클라우드 대신 사내 폐쇄망 환경에서 Ollama와 EXAONE 모델을 연동하여 보안성을 높이는 기획안 작성 필요")
    
    if st.button("보고서 초안 생성하기", key="btn_draft"):
        if not doc_project_name or not doc_core_content:
            st.warning("프로젝트명과 핵심 내용을 모두 입력해주세요.")
        else:
            with st.spinner("사내 지침을 반영하여 보고서 초안을 작성 중입니다..."):
                prompt = f"""
                당신은 사내 문서 작성 우수 직원입니다. 아래의 [사내 기준 규칙]을 철저히 준수하여, 신입사원이 바로 활용할 수 있는 깔끔한 보고서 초안을 작성해 주세요.
                - 형식은 반드시 [제목, 개요, 본문, 결론] 4단 구성을 지킬 것.
                - 프로젝트명({doc_project_name}), 작성자({doc_author}), 작성일자({doc_date})를 상단에 반드시 포함할 것.
                - 강압적인 어조(~해라, 당장 등)를 배제하고 객관적이고 정중한 서술어(~함, ~임)를 사용할 것.

                [사내 기준 규칙]
                {admin_guideline}

                [보고서 기본 정보]
                - 프로젝트명: {doc_project_name}
                - 작성자: {doc_author}
                - 작성일자: {doc_date}
                - 핵심 내용: {doc_core_content}
                """
                response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
                st.markdown("### 📄 생성된 보고서 초안")
                st.write(response['message']['content'])

# -------------------------------------------------------------
# 기능 2: 사내 규칙 기반 문서 점검
# -------------------------------------------------------------
with tab2:
    st.subheader("📝 사내 규칙 기반 문서 점검")
    st.markdown("작성한 문서를 파일로 업로드하거나 텍스트로 입력하여 사내 규칙에 맞는지 검사합니다.")
    
    input_method_1 = st.radio("문서 입력 방식 선택:", ["파일 업로드 (TXT, PDF)", "직접 텍스트 입력"], key="method1")
    target_doc_text_1 = ""
    
    if input_method_1 == "파일 업로드 (TXT, PDF)":
        uploaded_doc_1 = st.file_uploader("점검받을 문서를 업로드하세요", type=["txt", "pdf"], key="doc1")
        if uploaded_doc_1 is not None:
            if uploaded_doc_1.type == "text/plain":
                target_doc_text_1 = uploaded_doc_1.read().decode("utf-8")
            elif uploaded_doc_1.type == "application/pdf":
                reader = PdfReader(uploaded_doc_1)
                target_doc_text_1 = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.success("✅ 문서 로드 완료!")
    else:
        target_doc_text_1 = st.text_area("문서 내용을 직접 입력하세요:", height=200, placeholder="보고서 내용을 입력하세요...", key="area1")
    
    if st.button("문서 점검 시작", key="btn1"):
        if not target_doc_text_1:
            st.warning("문서 내용이나 파일을 입력해주세요.")
        else:
            with st.spinner("EXAONE이 사내 규칙과 대조하여 문서를 점검 중입니다..."):
                prompt = f"""
                당신은 사내 문서 감수 전문가입니다. 아래의 [사내 기준 규칙]을 참고하여, 사용자가 작성한 [작성 문서]를 검토해 주세요.
                규칙에 어긋난 부분, 누락된 항목, 잘못된 표현 등을 찾아내고 어떤 규칙을 위반했는지 친절하게 설명해 주세요.

                [사내 기준 규칙]
                {admin_guideline}

                [작성 문서]
                {target_doc_text_1}
                """
                response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
                st.markdown("### 📋 문서 점검 결과")
                st.write(response['message']['content'])

# -------------------------------------------------------------
# 기능 3: 사내·업계 용어 해설
# -------------------------------------------------------------
with tab3:
    st.subheader("💡 사내·업계 용어 해설 도우미")
    st.markdown("모르는 전문 용어나 사내 약어를 질문하면 AI가 실시간으로 설명해 줍니다.")
    
    term_input = st.text_input("궁금한 용어나 약어를 입력하세요 (예: RAG, 대외비, OJT 등):", key="term")
    
    if st.button("용어 설명 보기", key="btn2"):
        if not term_input:
            st.warning("용어를 입력해주세요.")
        else:
            with st.spinner("용어의 의미를 분석하는 중..."):
                prompt = f"""
                당신은 친절한 사내 교육 담당 멘토입니다. 신입사원이 이해하기 쉽도록 다음 용어나 약어에 대해 설명해 주세요.
                [질문 용어]
                {term_input}
                """
                response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
                st.markdown("### 📖 용어 해설 결과")
                st.write(response['message']['content'])

# -------------------------------------------------------------
# 기능 4: 문서 보안 위험도 판단
# -------------------------------------------------------------
with tab4:
    st.subheader("🛡️ 문서 보안 위험도 및 등급 판단")
    st.markdown("문서의 보안 등급(일반, 사내 공개, 대외비, 극비)을 판정하고 개인정보 포함 여부를 검토합니다.")
    
    input_method_3 = st.radio("문서 입력 방식 선택:", ["파일 업로드 (TXT, PDF)", "직접 텍스트 입력"], key="method3")
    target_doc_text_3 = ""
    
    if input_method_3 == "파일 업로드 (TXT, PDF)":
        uploaded_doc_3 = st.file_uploader("보안 검토할 문서를 업로드하세요", type=["txt", "pdf"], key="doc3")
        if uploaded_doc_3 is not None:
            if uploaded_doc_3.type == "text/plain":
                target_doc_text_3 = uploaded_doc_3.read().decode("utf-8")
            elif uploaded_doc_3.type == "application/pdf":
                reader = PdfReader(uploaded_doc_3)
                target_doc_text_3 = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            st.success("✅ 문서 로드 완료!")
    else:
        target_doc_text_3 = st.text_area("보안 검토할 문서 내용을 입력하세요:", height=200, placeholder="내용을 입력하세요...", key="area3")
    
    if st.button("보안 등급 평가", key="btn3"):
        if not target_doc_text_3:
            st.warning("문서 내용이나 파일을 입력해주세요.")
        else:
            with st.spinner("문서 보안 등급을 분석 중입니다..."):
                prompt = f"""
                당신은 보안 관리자입니다. 아래 문서를 분석하여 보안 등급을 [일반, 사내 공개, 대외비, 극비] 중 하나로 분류하고, 
                개인정보(주민번호, 연락처 등)나 내부 기밀 정보가 포함되어 있는지 검토하여 주의사항을 알려주세요.

                [분석할 문서]
                {target_doc_text_3}
                """
                response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
                st.markdown("### 🔒 보안 등급 및 위험도 진단")
                st.write(response['message']['content'])

# -------------------------------------------------------------
# 기능 5: PC 내부 문서 진짜 폴더 검색
# -------------------------------------------------------------
with tab5:
    st.subheader("🔍 PC 내부 문서 키워드 검색")
    st.markdown("사이드바에 지정한 **검색 폴더** 안의 실제 파일들을 스캔하여 키워드가 포함된 문서를 찾아줍니다.")
    
    search_query = st.text_input("찾고 싶은 내용이나 키워드를 입력하세요 (예: '보안 교육', '예산')", key="search")
    
    if st.button("문서 검색 실행", key="btn4"):
        if not search_query:
            st.warning("검색어를 입력해주세요.")
        elif not search_folder or not os.path.exists(search_folder):
            st.error("❌ 사이드바에서 올바른 'PC 문서 검색 폴더 경로'를 먼저 입력해주세요!")
        else:
            with st.spinner("PC 폴더 내 문서들을 스캔하고 검색하는 중..."):
                scanned_files = []
                for filename in os.listdir(search_folder):
                    file_path = os.path.join(search_folder, filename)
                    file_content = ""
                    if filename.endswith(".txt"):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_content = f.read()
                        except:
                            pass
                    elif filename.endswith(".pdf"):
                        try:
                            reader = PdfReader(file_path)
                            file_content = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
                        except:
                            pass
                    
                    if file_content:
                        scanned_files.append({"title": filename, "content": file_content})
                
                if not scanned_files:
                    st.warning("⚠️ 검색 폴더 안에 읽을 수 있는 TXT 또는 PDF 파일이 없습니다.")
                else:
                    files_str = "\n\n".join([f"[파일명: {f['title']}]\n내용 미리보기: {f['content'][:500]}..." for f in scanned_files])
                    prompt = f"""
                    사용자가 다음과 같이 문서를 찾고 있습니다: "{search_query}"
                    아래의 PC 폴더 내 실제 [파일 목록]을 분석하여, 사용자의 검색어와 가장 관련이 높은 파일을 찾고 어떤 내용 때문에 연관이 있는지 설명해 주세요.

                    [파일 목록]
                    {files_str}
                    """
                    response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
                    st.markdown("### 📂 진짜 폴더 검색 및 추천 결과")
                    st.write(response['message']['content'])