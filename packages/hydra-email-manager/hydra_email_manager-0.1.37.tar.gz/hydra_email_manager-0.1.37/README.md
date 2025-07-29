# Hydra Email Manager

Hydra Email Manager é uma biblioteca Python que facilita o envio e recebimento de emails utilizando a API do Microsoft Graph. A classe `HydraEmailManager` permite gerenciar emails de forma eficiente, oferecendo funcionalidades como verificação de senha, envio de emails com anexos, download de emails e obtenção de IDs de pastas.

## Instalação

Para instalar o Hydra Email Manager, você pode usar o pip:

```
pip install hydra_email_manager
```

## Uso

### Importando a classe

```python
from hydra_email_manager import HydraEmailManager
```

### Inicializando o gerenciador de emails

```python
email_manager = HydraEmailManager()
```

### Verificando a senha do usuário

```python
is_valid = email_manager.verificar_senha("usuario@example.com", "senha")
```

### Enviando um email

```python
email_manager.enviar_email(
    user_email="destinatario@example.com",
    user_from="remetente@example.com",
    subject="Assunto do Email",
    body="Corpo do email",
    attachment="caminho/para/anexo.txt"
)
```

### Baixando emails

```python
email_manager.baixar_emails(user_email="usuario@example.com", folder_id="ID_da_pasta")
```

### Obtendo IDs das pastas

```python
email_manager.obter_id_pastas(user_email="usuario@example.com")
```

## Testes

Os testes para a classe `HydraEmailManager` estão localizados no diretório `tests`. Para executar os testes, você pode usar o seguinte comando:

```
pytest tests/test_hydra_email_manager.py
```

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir um problema ou enviar um pull request.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.