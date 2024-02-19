import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import CognitiveServicesAccountCreateParameters
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.core.credentials import CognitiveServicesCredentials

# Carrega as variáveis de ambiente a partir do arquivo .env
from dotenv import load_dotenv
load_dotenv()

# Função para extrair texto de uma imagem
def extract_text(image_path, endpoint, subscription_key):
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    
    with open(image_path, "rb") as image_stream:
        result = computervision_client.recognize_printed_text_in_stream(image_stream, raw=True)
        return result

# Configurações do Azure
subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
resource_group_name = os.getenv('AZURE_RESOURCE_GROUP_NAME')
cognitive_services_account_name = os.getenv('AZURE_COGNITIVE_SERVICES_ACCOUNT_NAME')
location = os.getenv('AZURE_LOCATION')

# Autenticação usando as credenciais padrão do Azure
credential = DefaultAzureCredential()

# Cliente do Azure Resource Manager
resource_client = ResourceManagementClient(credential, subscription_id)

# Cliente do Azure Cognitive Services Management
cognitive_services_client = CognitiveServicesManagementClient(credential, subscription_id)

# Definição do modelo ARM
arm_template = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "resources": [
        {
            "type": "Microsoft.CognitiveServices/accounts",
            "apiVersion": "2023-10-01-preview",
            "name": "[parameters('accounts_DioLeituraImagens_name')]",
            "location": "eastus",
            "sku": {
                "name": "S0"
            },
            "kind": "CognitiveServices",
            "identity": {
                "type": "None"
            },
            "properties": {
                "apiProperties": {},
                "customSubDomainName": "dioleituraimagens".lower(),
                "networkAcls": {
                    "defaultAction": "Allow",
                    "virtualNetworkRules": [],
                    "ipRules": []
                },
                "publicNetworkAccess": "Enabled"
            }
        }
    ]
}

# Nome do grupo de recursos
resource_group = resource_client.resource_groups.create_or_update(
    resource_group_name,
    {"location": location}
)

# Implantar o modelo ARM
deployment_properties = {
    "mode": "Incremental",
    "template": arm_template,
}

deployment_async_operation = resource_client.deployments.begin_create_or_update(
    resource_group_name,
    "deployCognitiveServices",
    deployment_properties
)

deployment_async_operation.wait()

# Recuperar informações da conta do Cognitive Services após a implantação
cognitive_services_account = cognitive_services_client.accounts.get_properties(
    resource_group_name,
    cognitive_services_account_name
)

# Obter o ponto de extremidade e a chave
endpoint = cognitive_services_account.endpoint
subscription_key = os.getenv('AZURE_SUBSCRIPTION_KEY')

# Caminho para a imagem (substitua pelo caminho real)
image_path = 'inputs/Direitos-autorais-900x600.jpg'
# Extrai o texto da imagem
result = extract_text(image_path, endpoint, subscription_key)

# Imprime o texto extraído
print("Texto extraído da imagem:")
print(result.read())

# Salvar o resultado do texto em um arquivo de texto
output_text_path = os.path.join('output', 'result.txt')
os.makedirs('output', exist_ok=True)
with open(output_text_path, 'wb') as output_text_file:
    output_text_file.write(result.read())

# Copiar a imagem de entrada para a pasta de saída
output_image_path = os.path.join('output', 'input_image.jpg')
os.replace(image_path, output_image_path)

print(f"Resultado do texto salvo em: {output_text_path}")
print(f"Imagem de entrada copiada para: {output_image_path}")
