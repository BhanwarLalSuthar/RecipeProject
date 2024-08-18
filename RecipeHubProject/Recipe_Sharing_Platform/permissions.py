from rest_framework.permissions import BasePermission, SAFE_METHODS


# class IsAuthorOrReadOnly(BasePermission):
#     """
#     Custom permission to only allow authors of an article to edit or delete it.
#     """

    # def has_permission(self, request, view):
    #     # Allow any user to retrieve articles
    #     if request.method in SAFE_METHODS:
    #         return True
    #     # Allow any authenticated user to create articles
    #     if request.method == 'POST':
    #         return request.user.is_authenticated
    #     # Otherwise, only allow access to authors
    #     return False

    # def has_object_permission(self, request, view, obj):
    #     # Allow any user to retrieve articles
    #     if request.method in SAFE_METHODS:
    #         return True
    #     # Otherwise, only allow access to the author
    #     return obj.author == request.user
class IsAuthor(BasePermission):
    """
    Custom permission to only allow authors of an article to edit or delete it.
    """
 
    def has_permission(self, request, view):
        # print(request.author.user_type)
        return request.user.is_authenticated and request.author.user_type == "author"
        
class IsCustomer(BasePermission):
    """
    Custom permission to only allow authors of an article to edit or delete it.
    """
 
    def has_permission(self, request, view):
        return request.author.user_type == "customer"
        