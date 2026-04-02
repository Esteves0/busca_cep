document.addEventListener('DOMContentLoaded', () => {

    const cepInput = document.getElementById('cep-input');
    const searchBtn = document.getElementById('search-btn');
    const btnText = searchBtn.querySelector('span');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const errorMsg = document.getElementById('error-message');


    const resCep = document.getElementById('res-cep');
    const resStreet = document.getElementById('res-street');
    const resNeighborhood = document.getElementById('res-neighborhood');
    const resCity = document.getElementById('res-city');
    const resState = document.getElementById('res-state');
    const resComplement = document.getElementById('res-complement');
    const resIbge = document.getElementById('res-ibge');
    const sourceBadge = document.getElementById('source-badge');


    cepInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 5) {
            value = value.substring(0, 5) + '-' + value.substring(5, 8);
        }
        e.target.value = value;
    });


    const searchCep = async () => {
        const cep = cepInput.value.replace(/\D/g, '');

        if (cep.length !== 8) {
            showError('Por favor, informe um CEP válido com 8 dígitos!');
            return;
        }

        setLoading(true);
        hideError();
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch(`/api/consulta/${cep}`);
            const result = await response.json();


            if (response.ok) {
                displayResult(result);
            } else {
                showError(result.error || 'Erro ao buscar CEP');
            }
        } catch (error) {
            showError('Erro de conexão com o servidor.');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };


    const displayResult = (result) => {
        const data = result.data;
        const source = result.source;

        resCep.textContent = data.cep.replace(/(\d{5})(\d{3})/, '$1-$2');
        resStreet.textContent = data.rua || 'Não Informado';
        resNeighborhood.textContent = data.bairro || 'Não Informado';
        resCity.textContent = data.cidade || 'Não Informado';
        resState.textContent = data.estado || 'Não Informado';
        resComplement.textContent = data.complemento || 'Não Informado';
        resIbge.textContent = data.ibge || 'N/A';


        sourceBadge.textContent = source === 'local.db' ? 'BANCO LOCAL' : 'API EXTERNA';
        sourceBadge.className = 'badge ' + (source === 'local.db' ? 'badge-db' : 'badge-api');

        resultContainer.classList.remove('hidden');
    };


    const setLoading = (isLoading) => {
        if (isLoading) {
            btnText.classList.add('hidden');
            loader.style.display = 'block';
            searchBtn.disabled = true;
        } else {
            btnText.classList.remove('hidden');
            loader.style.display = 'none';
            searchBtn.disabled = false;
        }
    };


    const showError = (message) => {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    };

    const hideError = () => {
        errorMsg.classList.add('hidden');
    };


    searchBtn.addEventListener('click', searchCep);

    cepInput.addEventListener('keypress', (ev) => {
        if (ev.key === 'Enter') {
            searchCep();
        }
    });
});