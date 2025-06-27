from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import PerfilSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario creado correctamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class PerfilAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PerfilSerializer(request.user)
        return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    user = request.user
    perfil = user.perfilusuario  # usa tu modelo extendido
    return Response({
        'username': user.username,
        'email': user.email,
        'tipo_cuenta': perfil.tipo_cuenta
    })




