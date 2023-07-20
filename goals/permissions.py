from rest_framework import permissions

from goals.models import BoardParticipant, Board, GoalCategory
import logging
logger = logging.getLogger(__name__)

class BoardPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()

        is_owner = BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()

        logger.info(f"User {request.user.id} is trying to edit board {obj.id}, is owner: {is_owner}")

        return is_owner


class GoalPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user,
                board=obj.category.board
            ).exists()

        return BoardParticipant.objects.filter(
            user=request.user,
            board=obj.category.board,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists()



class GoalCategoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        logger.info(request.data)
        if request.method == 'POST':
            category_id = request.data.get('category')
            if category_id is None:
                return False
            category = GoalCategory.objects.filter(id=category_id).first()
            if category is None:
                return False
            return BoardParticipant.objects.filter(
                user=request.user,
                board=category.board,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
            ).exists()
        else:
            return True


class GoalCommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            board = Board.objects.filter(participants__user__goal=request.data['goal'])
            return BoardParticipant.objects.filter(
                user=request.user,
                board__in=board,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
            ).exists()
        else:
            return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user,
                board=obj.goal.category.board
            ).exists()

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return (obj.user == request.user and BoardParticipant.objects.filter(
                            user=request.user,
                            board=obj.goal.category.board,
                            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
                        ).exists()
                    )
