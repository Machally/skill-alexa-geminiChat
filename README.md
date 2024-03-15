# Alexa GeminiChat
### Modelo de Skill Alexa para integrar o Google Gemini nos dispositivos Alexa

**Visite o cana [Scintilla Hub](https://www.youtube.com/@scintillahub) no YouTube**

## Requisitos
* Com uma conta Google gere uma chave de autenticação API site da [Google AI Developer](https://ai.google.dev/). Copie e guarde a chave, elá só será visível no instante da criação.
* Crie uma conta na [Amazon](https://www.amazon.com/ap/signin?openid.pape.preferred_auth_policies=Singlefactor&clientContext=132-2293245-7926858&openid.pape.max_auth_age=7200000&openid.return_to=https%3A%2F%2Fdeveloper.amazon.com%2Falexa%2Fconsole%2Fask&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=amzn_dante_us&openid.mode=checkid_setup&marketPlaceId=ATVPDKIKX0DER&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&) e realize o login no _Alexa Developer Console_.
## Criando a Skill Alexa
Crie uma Skill Alexa-hosted (Python) na Alexa: (_Create Skill_)

1. Name your Skill: Escolha um nome de sua preferência (Ex: GeminiGPT)
2. Choose a primary locale: Portuguese (BR)
3. Clique em _Next_. Em tipo de experiência selecione: Other > Custom > _Alexa-hosted (Python)_
4. _Hosting region_: Pode deixar o padrão _US East (N. Virginia)_
5. Em _Templates_: Clique em _Import Skill_
6. Insira o endereço do repositório: https://github.com/Machally/skill-alexa-geminiChat.git e confirme.

## Configurando a Skill
Ao finalizar a importação em _Invocations_ > _Skill Invocation Name_:
1. Edite _Skill Invocation Name_. Este será o comando de invocação para sua skill. Se atende para os requisitos e restrições de palavras
2. Clique em _Save_
3. Realize o Build da Skill clicando em _Build Skill_. Ao finalizar, vá para a aba **Code**
4. Crie um arquivo dentro da pasta Lambda chamado _.env_ e adicione a linha, adicionando a API key gerada:
   ```shell
   GOOGLE_API_KEY=SuaApiKeyGoogleAI
   ```
5. Clique em _Save_ e então em _Deploy_
   
## Teste da Skill
Ao finalizar o _deploy_ vá para aba **Test**:
1. Em _Skill testing is enabled in_ mude de _Off_ para _Development_
2. Para usar comandos de voz aceite a requisição de uso do microfone pelo site, e para falar clique e segure o ícone de mic, e solte para enviar
3. Use comando de ativação configurado para iniciar a Skill, e pronto está interagindo com o Gemini pela Alexa!

A Skill já estará disponível em todos os dispositivos Alexa vinculados a sua conta.
