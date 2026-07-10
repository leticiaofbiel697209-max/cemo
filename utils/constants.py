PERFIS = ["administrador", "gestor", "compras", "estoque", "laboratório", "consulta", "auditoria"]

PERMISSOES = {
    "administrador": {"*"},
    "gestor": {"dashboard", "insumos", "compras", "processos", "atas", "alertas", "relatorios", "configuracoes"},
    "compras": {"dashboard", "insumos", "compras", "processos", "atas", "alertas", "relatorios"},
    "estoque": {"dashboard", "insumos", "estoque", "alertas", "relatorios"},
    "laboratório": {"dashboard", "insumos", "compras", "processos", "alertas"},
    "consulta": {"dashboard", "insumos", "relatorios"},
    "auditoria": {"dashboard", "auditoria", "relatorios", "alertas"},
}

ETAPAS_PROCESSO = [
    "solicitação",
    "validação técnica",
    "compras",
    "pesquisa de preços",
    "aprovação",
    "licitação",
    "empenho",
    "pedido emitido",
    "aguardando entrega",
    "recebido",
    "concluído",
    "cancelado",
]

TIPOS_MOVIMENTACAO = ["entrada", "saída", "ajuste", "perda", "devolução", "inventário"]
NIVEIS_ALERTA = ["crítico", "alto", "médio", "informativo"]
