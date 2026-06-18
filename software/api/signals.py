import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Produto, Pedido

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Produto)
def alertar_estoque_minimo(sender, instance, **kwargs):
    if instance.estoque <= instance.estoque_minimo:
        logger.warning(
            f"ALERTA DE STOCK: O produto '{instance.nome}' (SKU: {instance.sku}) "
            f"atingiu ou está abaixo do stock mínimo! Atual: {instance.estoque}, Mínimo: {instance.estoque_minimo}"
        )

@receiver(pre_save, sender=Pedido)
def alertar_mudanca_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            pedido_antigo = Pedido.objects.get(pk=instance.pk)
            if pedido_antigo.status != instance.status:
                payload_notificacao = {
                    "cliente_id": instance.cliente.id,
                    "cliente_email": instance.cliente.email,
                    "pedido_numero": instance.numero,
                    "status_antigo": pedido_antigo.status,
                    "status_novo": instance.status,
                    "mensagem": f"O seu pedido {instance.numero} mudou para: {instance.get_status_display()}"
                }
                logger.info(f"NOTIFICAÇÃO CLIENTE PREPARADA: {payload_notificacao}")
                
                from .models import Notificacao
                from django.core.mail import send_mail
                from django.conf import settings
                
                titulo = f"Atualização do Pedido #{instance.numero}"
                mensagem = f"O estado do seu pedido passou para: {instance.get_status_display()}"
                
                Notificacao.objects.create(
                    usuario=instance.cliente.user,
                    titulo=titulo,
                    mensagem=mensagem
                )
                
                if instance.cliente.email:
                    try:
                        send_mail(
                            subject=titulo,
                            message=mensagem,
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contato@hortaviva.com'),
                            recipient_list=[instance.cliente.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Erro ao enviar email: {e}")
        except Pedido.DoesNotExist:
            pass
