from app.modules.chat.chat_schemas import ChatAnalysis, ChatDecision
from app.modules.knowledge.knowledge_service import knowledge_service


class ReplyService:
    def build_reply(self, analysis: ChatAnalysis, decision: ChatDecision) -> str:
        product_name = self._get_product_name(analysis.product)

        if analysis.blocked:
            return self._blocked_reply(analysis)

        if "tema_medico" in analysis.safety_flags:
            return self._medical_safe_reply()

        if decision.action == "escalar_humano":
            return self._human_escalation_reply(analysis)

        if decision.action == "crear_borrador_cotizacion":
            return self._quote_draft_reply(product_name)

        if decision.action == "pedir_datos":
            return self._missing_data_reply(analysis, product_name)

        if analysis.intent == "precio":
            return self._price_reply(product_name)

        if analysis.intent == "envio":
            return self._shipping_reply()

        if analysis.intent == "informacion_producto":
            return self._product_info_reply(analysis)

        if analysis.intent == "saludo":
            return self._greeting_reply()

        return self._default_reply()

    def _get_product_name(self, product_id: str | None) -> str | None:
        if product_id is None:
            return None

        product = knowledge_service.get_product_by_id(product_id)

        if product is None:
            return None

        return product.name

    def _blocked_reply(self, analysis: ChatAnalysis) -> str:
        if "pulque_menor_edad" in analysis.safety_flags:
            return (
                "Lo siento, no podemos apoyar con la venta de pulque a menores de edad. "
                "Por seguridad y cumplimiento, esta solicitud no puede continuar."
            )

        return (
            "Lo siento, no podemos continuar con esta solicitud por reglas de seguridad. "
            "Si consideras que se trata de un error, podemos canalizarlo con una persona del equipo."
        )

    def _medical_safe_reply(self) -> str:
        return (
            "La miel de maguey puede usarse como alternativa natural para endulzar alimentos o bebidas, "
            "pero no debe considerarse un tratamiento medico ni una cura. "
            "Para temas de salud, lo recomendable es consultar a un profesional."
        )

    def _human_escalation_reply(self, analysis: ChatAnalysis) -> str:
        if "alto_volumen" in analysis.safety_flags:
            return (
                "Gracias por escribir a AgroAvis. Por el volumen que solicitas, "
                "vamos a canalizar tu caso con una persona del equipo para preparar una cotizacion adecuada. "
                "Por favor comparte presentacion, zona de entrega, fecha requerida, si necesitas factura "
                "y un telefono de contacto."
            )

        if analysis.intent in ["reclamo", "reembolso"]:
            return (
                "Lamento el inconveniente. Para revisar tu caso correctamente, "
                "lo vamos a canalizar con una persona del equipo. "
                "Por favor comparte tu numero de pedido, nombre de compra y un medio de contacto."
            )

        return (
            "Gracias por escribir a AgroAvis. Para atender tu caso correctamente, "
            "lo vamos a canalizar con una persona del equipo. "
            "Por favor comparte los datos necesarios para darle seguimiento."
        )

    def _quote_draft_reply(self, product_name: str | None) -> str:
        if product_name is None:
            product_name = "el producto solicitado"

        return (
            f"Perfecto, ya tengo los datos principales para preparar un borrador de cotizacion de {product_name}. "
            "El siguiente paso es revisar disponibilidad, logistica y condiciones comerciales antes de confirmar."
        )

    def _missing_data_reply(self, analysis: ChatAnalysis, product_name: str | None) -> str:
        if analysis.intent == "cotizacion_mayoreo":
            if product_name is None:
                product_name = "el producto que necesitas"

            return (
                f"Claro, con gusto te apoyamos con una cotizacion de mayoreo para {product_name}. "
                "Para prepararte una propuesta correcta, por favor confirma: "
                "presentacion que necesitas, zona de entrega, fecha requerida, "
                "si necesitas factura y un telefono de contacto."
            )

        if analysis.intent == "precio":
            return self._price_reply(product_name)

        if analysis.intent == "envio":
            return self._shipping_reply()

        return (
            "Con gusto te ayudo. Para continuar correctamente, por favor comparte los datos faltantes: "
            f"{', '.join(analysis.missing_data)}."
        )

    def _price_reply(self, product_name: str | None) -> str:
        if product_name is None:
            return (
                "Con gusto te ayudo con el precio. Para darte informacion correcta, "
                "confirmame el producto, cantidad, presentacion y zona de entrega."
            )

        return (
            f"Con gusto te ayudo con el precio de {product_name}. "
            "Para darte informacion correcta, confirmame cantidad, presentacion y zona de entrega."
        )

    def _shipping_reply(self) -> str:
        return (
            "Si podemos revisar la entrega segun tu zona. "
            "Comparteme el producto, cantidad y municipio o ciudad de entrega."
        )

    def _product_info_reply(self, analysis: ChatAnalysis) -> str:
        if analysis.product is not None:
            product = knowledge_service.get_product_by_id(analysis.product)

            if product is not None:
                return (
                    f"{product.name}: {product.description} "
                    "No debe considerarse un tratamiento medico. "
                    "Si gustas, te puedo orientar segun el uso que le quieras dar."
                )

        return (
            "La miel de maguey puede usarse como alternativa natural para endulzar "
            "bebidas, postres y alimentos. No debe considerarse un tratamiento medico. "
            "Si gustas, te puedo orientar segun el uso que le quieras dar."
        )

    def _greeting_reply(self) -> str:
        return (
            "Hola, gracias por escribir a AgroAvis. "
            "Con gusto te ayudo. Manejamos productos derivados del maguey, "
            "como miel de maguey, aguamiel, pulque y penca de maguey, "
            "segun disponibilidad."
        )

    def _default_reply(self) -> str:
        return (
            "Gracias por escribir a AgroAvis. Con gusto te ayudo. "
            "Por favor dime que producto te interesa, en que cantidad y para que zona seria la entrega."
        )


reply_service = ReplyService()
