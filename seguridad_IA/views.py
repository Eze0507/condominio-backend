import time, requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import LecturaPlaca
from .serializers.serializersPlaca import LecturaPlacaSerializer
from residencial.modelsVehiculo import Vehiculo

PLATE_URL = "https://api.platerecognizer.com/v1/plate-reader/"

class AlprScanView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        token = settings.PLATE_TOKEN
        if not token:
            return Response({"error": "Configura PLATE_TOKEN"}, status=500)

        f = request.FILES.get("upload")
        if not f:
            return Response({"error": "Debes enviar el archivo en 'upload'."}, status=400)
        if not getattr(f, "content_type", "").startswith("image/"):
            return Response({"error": "El archivo debe ser una imagen."}, status=400)

        camera_id = request.data.get("camera_id", "") or ""
        regions   = request.data.get("regions") or settings.PLATE_REGIONS

        headers = {"Authorization": f"Token {token}"}
        payload = {"regions": regions}
        if camera_id:
            payload["camera_id"] = camera_id

        files = {"upload": (getattr(f, "name", "frame.jpg"), f, getattr(f, "content_type", "image/jpeg"))}
        try:
            f.seek(0)
            r = requests.post(PLATE_URL, headers=headers, data=payload, files=files, timeout=20)
            if r.status_code == 429:
                time.sleep(1)
                f.seek(0)
                r = requests.post(PLATE_URL, headers=headers, data=payload, files=files, timeout=20)
        except requests.RequestException as e:
            return Response({"error": "No se pudo contactar al ALPR", "detail": str(e)}, status=502)

        # 🔧 ACEPTAR 200/201 COMO ÉXITO
        if r.status_code not in (200, 201):
            return Response({"error": "ALPR no respondió OK", "status_code": r.status_code, "detail": r.text}, status=r.status_code)

        js = r.json()
        results = js.get("results", [])

        if not results:
            l = LecturaPlaca.objects.create(placa="", score=0.0, camera_id=camera_id, image_url=None, vehiculo=None, match=False)
            return Response({
                "status": "no-plate-found",
                "plate": None, "score": None, "match": False,
                "vehiculo": None,
                "lectura": LecturaPlacaSerializer(l).data
            }, status=200)

        best      = max(results, key=lambda x: x.get("score", 0) or 0.0)
        plate_raw = (best.get("plate") or "").upper()
        score     = float(best.get("score") or 0.0)

        v_match = (Vehiculo.objects.filter(placa__iexact=plate_raw)   # BD ya normalizada
                .select_related("persona")
                .first())

        lectura = LecturaPlaca.objects.create(
            placa=plate_raw, score=score, camera_id=camera_id,
            image_url=None, vehiculo=v_match, match=bool(v_match)
        )

        from residencial.serializers.serializersVehiculo import VehiculoSerializer
        return Response({
            "status": "ok",
            "plate": plate_raw,
            "score": score,
            "match": bool(v_match),
            "vehiculo": VehiculoSerializer(v_match).data if v_match else None,
            "lectura": LecturaPlacaSerializer(lectura).data
        }, status=200)




