# Crypto-PT

`crypto-pt` é uma biblioteca Python simples, com foco no público de língua portuguesa, para criptografia e descriptografia de strings usando o algoritmo RSA.

## Funcionalidades

* Geração de chaves RSA (pública e privada) com tamanho de bits personalizável (recomenda-se 1024 bits para maior segurança).
* Criptografia de strings.
* Descriptografia de mensagens criptografadas.

## Instalação

Você pode instalar `crypto-pt` via pip:

```bash
pip install crypto-pt
```

## Como Usar

Aqui está um exemplo básico de como usar a biblioteca:

```python
import crypto_pt

# 1. Defina a mensagem e o tamanho dos bits para as chaves
mensagem_original = "Minha mensagem secreta em português!"
bits_chave = 512  # Para testes rápidos. Use 1024 ou 2048 para maior segurança.

print(f"Mensagem original: {mensagem_original}")

# 2. Gere as chaves pública e privada
try:
    chave_publica, chave_privada = crypto_pt.gerar_chaves_grandes(bits=bits_chave)
    print(f"Chave Pública (e, n): {chave_publica}")
    print(f"Chave Privada (d, n): {chave_privada}")

    # 3. Criptografe a mensagem
    mensagem_criptografada = crypto_pt.criptografar(mensagem_original, chave_publica)
    print(f"Mensagem Criptografada: {mensagem_criptografada}")

    # 4. Descriptografe a mensagem
    mensagem_descriptografada = crypto_pt.descriptografar(mensagem_criptografada, chave_privada)
    print(f"Mensagem Descriptografada: {mensagem_descriptografada}")

    assert mensagem_original == mensagem_descriptografada
    print("Criptografia e descriptografia bem-sucedidas!")

except ValueError as e:
    print(f"Erro: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")

```

## Licença

Este projeto é licenciado sob a Licença MIT - veja o arquivo `LICENSE` para detalhes.

## Aviso

Esta implementação de RSA é para fins educacionais e pode não ser segura para uso em produção sem uma auditoria de segurança completa e a implementação de esquemas de preenchimento (padding schemes) adequados como OAEP. Para aplicações de segurança críticas, considere usar bibliotecas de criptografia bem estabelecidas e revisadas pela comunidade.