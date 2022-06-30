from typing import Any, TypeVar
from django.db.models import Model, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q, QuerySet
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from .models import (
    DiversityFocus,
    Organization,
    Location,
    TechnologyFocus,
    SuggestedEdit,
    ViolationReport,
)
from .forms import (
    OrgForm,
    CreateOrgForm,
    SuggestEditForm,
    ViolationReportForm,
)

def is_organizer(user: object, org:object) -> bool:
    """Check if a user is authenticated and an organizer of an organization.

    Args:
        user (object):
        org (object):

    Returns:
        bool

    """
    if not user.is_authenticated:
        return False

    if org.parent and user in org.parent.organizers.all():
        return True

    if user in org.organizers.all():
        return True

    if user.is_superuser:
        return True
    
    return False

_context = TypeVar('_context', bound=dict)

# Create your views here.
class HomePageView(ListView):
    """
    The Home Page showing featured organizations and a map of all organizations.

    Inheritance:
        ListView: Base class for generic views that display a list of objects.

    """
    
    template_name = "home.html"
    model = Organization


    def get_queryset(self) -> QuerySet[Organization]:
        """Return the organizations where the is_featured flag is True."""
        return self.model.objects.filter(is_featured=True) \
            .exclude(parent=None).values('parent__name', 'parent__slug') \
            .distinct().order_by()

    def get_context_data(self, **kwargs) -> _context:
        """
        Add aggregations from the object_list and the map API call trigger for `is_featured=True`
        """        

        context = super().get_context_data(**kwargs)

        context['aggs'] = [self.model.objects.get(name=obj['parent__name']) for obj in self.object_list]
        context["map"] = "is_featured=True"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY
        return context


class SearchResultsView(ListView):
    """
    Returns the results of a search query.

    Inheritance:
        ListView: Base class for generic views that display a list of objects.

    """
    template_name = "search_results.html"
    model = Organization

    def get_queryset(self) -> SearchQuery:
        """
        Test search based on existed entrys in the database.
        Checks Organization, Location, DiversityFocus and TechnologyFocus objects.
        Returns a full text search on those models if nothing is a match.

        Args:
            self (undefined):

        Returns:
            SearchQuery: The query object
        """
        
        query = self.request.GET.get("q")

        if name_match := Organization.objects.filter(name__iexact=query):
            return name_match

        if name_match := Organization.objects.filter(name__icontains=query):
            return name_match

        if location_match := Organization.objects.filter(
            Q(location__name=query) | Q(location__region=query) | Q(location__country=query)
        ):
            return location_match

        if diversity_match := Organization.objects.filter(diversity_focus__name=query):
            return diversity_match

        if techonology_match := Organization.objects.filter(technology_focus__name=query):
            return techonology_match

        # Create vectors for search
        query = SearchQuery(self.request.GET.get("q"), search_type="websearch")
        vector = (
            SearchVector("diversity_focus__name", weight="B")
            + SearchVector("technology_focus__name", weight="B")
            + SearchVector("location__name", weight="C")
            + SearchVector("location__region", weight="C")
            + SearchVector("location__country", weight="C")
        )
        queryset = (
            Organization.objects.annotate(
                rank=SearchRank(vector, query, weights=[0.1, 0.3, 0.6, 1.0]),
            )
            .filter(rank__gte=0.4)
            .order_by("-rank")
            .distinct()
        )
        return queryset

    def get_context_data(self, **kwargs) -> _context:
        """
        Add the search query and the parents aggregates to the context.
        """
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["parents"] = self.object_list.values("parent__name").distinct()
        return context


class OrgListView(ListView):
    """
    Returns a list of all organizations.

    Inheritance:
        ListView: base class for generic views that display a list of objects.
    """
    template_name = "org_list.html"
    model = Organization


class OrgDetailView(DetailView):
    """
    Returns an organization's detail page.

    Inheritance:
        DetailView: base class for generic views that display a list of objects.
    """
    template_name = "orgs/detail.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_context_data(self, **kwargs) -> _context:
        """
        Add the organization's parent and children to the context.
        Enable the map for all of the orgs children.
        Uses focuses and focus parents to build similar organizations.
        """
        context = super().get_context_data(**kwargs)
        context['is_organizer'] = is_organizer(self.request.user, self.object) or self.request.user.is_superuser

        if children := self.model.objects.filter(parent=self.object):
            context["children"] = children.order_by("location__country", "location__name")
            context["map"] = f"parent={self.object.pk}"
            context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY
            
        else:
            diversity_focuses = []

            for focus in self.object.diversity_focus.all():
                if focus.parents:
                    for parent in focus.parents.all():
                        diversity_focuses.append(parent)

            diversity_focuses.extend(self.object.diversity_focus.all())
            technology_focuses = []
            for focus in self.object.technology_focus.all():
                if focus.parents:
                    for parent in focus.parents.all():
                        technology_focuses.append(parent)
            technology_focuses.extend(self.object.technology_focus.all())

            other_orgs = self.model.objects.filter(
                location=self.object.location,
            ).exclude(pk=self.object.pk)

            if diversity_focuses:
                other_orgs = other_orgs.filter(diversity_focus__in=diversity_focuses)

            if technology_focuses:
                other_orgs = other_orgs.filter(technology_focus__in=technology_focuses)
            context["other_orgs"] = other_orgs.distinct()
        return context


class CreateOrgView(LoginRequiredMixin, CreateView):
    """
    Create a new organization.

    Inheritance:
        LoginRequiredMixin: Requires the user to be logged in.
        CreateView: The Django view for creating a new object.
    """
    template_name = "orgs/create.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_success_url(self) -> str:
        """
        return the absolute url of the new organization.

        Returns:
            str: url of the new organization
        """
        return self.object.get_absolute_url()

    def post(self) -> HttpResponse:
        """
        Override the post method to add the user to the organization's list of organizers.

        Returns:
            HttpResponse: The page at the url of the new organization.
        """
        super().post()
        self.object.organizers.add(self.request.user)
        self.object.save()
        return redirect(self.get_success_url())


class SuggestEditView(UpdateView):
    """
    Form that allows users to suggest edits to an organization page.

    Inheritance:
        UpdateView (_type_): Django BaseView for updating an object.code
    """
    template_name = "orgs/update.html" # TODO:Create #20 Custom Template
    form_class = SuggestEditForm
    model = Organization 

    def get_success_url(self) -> str:
        """
        Return the absolute url of the organization.

        Returns:
            str: url of the organization
        """
        return self.object.get_absolute_url()
    
    def get_initial(self, *args, **kwargs) -> dict[str, Any]:
        """
        List all the tags, and organizers for the organization.

        Returns:
            dict[str, Any]: The initial data to pass into the form.
        """
        initial = super().get_initial(*args, **kwargs)
        initial["diversity_focus"] = (", ").join([x.name for x in self.object.diversity_focus.all()])
        initial["technology_focus"] = (", ").join([x.name for x in self.object.technology_focus.all()])
        initial["organizers"] = (", ").join([x.email for x in self.object.organizers.all()]) # TODO: #22 REMOVE NEED FOR THIS
        if self.object.location:
            location_fields = (
                self.object.location.name,
                self.object.location.region,
                self.object.location.country,
            )
            initial['location'] = ", ".join([x for x in location_fields if x])
        if self.object.parent:
            initial['parent'] = self.object.parent.name
    
        return initial

    def form_valid(self) -> HttpResponse:
        """
        Override the form_valid method to add the user to the suggested edit.

        Returns:
            HttpResponse: The page at the url of the organization.
        """
        user = self.request.user if self.request.user.is_authenticated else None
        report = dict(self.request.POST)
        report.pop("csrfmiddlewaretoken", None)
        report = SuggestedEdit(
            organization=self.object,
            report=report,
            user=user,
            )
        
        report.save()
        return redirect(self.get_success_url())


class ReportViolationView(CreateView):
    """
    View that allows users to report a violation of an organization.

    Inheritance:
        CreateView: Django BaseView for creating an object.
    """
    template_name = "orgs/report.html" # TODO:Create Custom Template
    form_class = ViolationReportForm
    model = ViolationReport

    def get_success_url(self) -> str:
        """
        Return the absolute url of the organization.

        Returns:
            str: absolute url of the organization
        """
        return self.object.get_absolute_url()

    def get_context_data(self, *args, **kwargs) -> _context:
        """Add the organization to the context"""
        context = super().get_context_data(*args, **kwargs)
        context["organization"] = Organization.objects.get(slug=self.kwargs['slug'])
        return context

    def form_valid(self, form: object) -> str:
        """
        Override the form_valid method to add the organization and user to the violation report 
        prior to returning the success_url

        Args:
            form (object): the form object

        Returns:
            str: success_url of the organization
        """
        obj = form.save(commit=False)
        obj.organization = Organization.objects.get(slug=self.kwargs['slug'])
        obj.user = self.request.user if self.request.user.is_authenticated else None
        return super().form_valid(form)
        

class UpdateOrgView(LoginRequiredMixin, UpdateView):
    """
    Update an existing organization.

    Inheritance:
        LoginRequiredMixin: Requires the user to be logged in.
        UpdateView: Django BaseView for updating an object.
    """
    template_name = "orgs/update.html"
    model = Organization
    form_class = OrgForm

    def get_initial(self, *args, **kwargs) -> dict[str, Any]:
        """
        Return the tags and organizers as strings in the form data.

        Returns:
            dict: initial data
        """
        initial = super().get_initial(*args, **kwargs)
        initial["diversity_focus"] = (", ").join([x.name for x in self.object.diversity_focus.all()])
        initial["technology_focus"] = (", ").join([x.name for x in self.object.technology_focus.all()])
        initial["organizers"] = (", ").join([x.email for x in self.object.organizers.all()])
    
        if self.object.parent:
            initial['parent'] = self.object.parent.name
    
        # Return the fetched data from Azure Maps instead of the supplied data from the users (initially)
        if self.object.location:
            location_fields = (
                self.object.location.name,
                self.object.location.region,
                self.object.location.country,
            )
            initial['location'] = ", ".join([x for x in location_fields if x])
        
        return initial
        
    def dispatch(self, request: object, *args, **kwargs) -> object:
        """
        Raise a 404 if user is not an organizer

        Args:
            request : the request object

        Raises:
            Http404: if user is not an organizer

        Returns:
            object: the default dispatch object
        """
        #TODO: #23 Can this be a TestMixin instead?

        if  is_organizer(request.user, self.get_object()):
            return super().dispatch(request, *args, **kwargs)
        raise Http404("You must be an organization member to update an organization.")
        

class ClaimOrgView(LoginRequiredMixin, DetailView):
    """
    Claim an organization if there are no organizers. This request must be reviewed.
    The DetailView is to gain access to the Organization object.

    Inheritance:
        LoginRequiredMixin (object): Requires the user to be logged in.
        DetailView (): Django BaseView for displaying a detail of an object.

    Returns:
        _type_: _description_

    TODO: Create a type request for suggested edits and make claiming an org as an option.
    """
    template_name = "orgs/claim.html"
    model = Organization

    def post(self, request: object, *args, **kwargs) -> str:
        """
        Override the post method to add the user to the organization as an organizer.

        WARNING: The logic for adding the user to the organization as an organizer has currently not been implemented and this should be live.

        Args:
            request (object): the request object

        Returns:
            str: the absolute url of the organization
        """
        self.object = self.get_object()

        if form.is_valid and request.user.is_authenticated:    
             # self.object.organizers.add(request.user)  DO NOT DO THIS AS IT WILL AUTOMATICALLY ADD THE USER AS AN ORGANIZER
            self.object.save()

        return redirect(self.object.get_absolute_url())


class LocationFilterView(ListView):
    """
    Filter the organizations by location.

    Inheritance:
        ListView: Django BaseView for displaying a list of objects.
    """
    template_name = "orgs/list.html"
    model = Organization

    def get_queryset(self) -> object:
        """
        Filter the organizations by location.

        Returns:
            object: QuerySet of organizations
        """
        return Organization.objects.filter(location__pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs) -> _context:
        """Add the location to the context."""
        context = super().get_context_data(**kwargs)
        context["location"] = Location.objects.get(pk=self.kwargs["pk"])
        return context


class DiversityFocusView(ListView):
    """
    List of the diversity focuses.

    Inheritance:
        ListView: Django BaseView for displaying a list of objects.
    """
    template_name = "tags/list.html"
    model = DiversityFocus
    paginate_by=50

    def get_context_data(self, **kwargs) -> _context:
        """
        Add a focus and focus_filter to the context.
        This can be used to distinguish diversity focuses from other tags.
        """
        context = super().get_context_data(**kwargs)
        context['focus'] = 'diversity'
        context['focus_filter'] = 'diversity_filter'
        return context


class DiversityFocusFilterView(ListView):
    """
    List organizations based on the diversity focus.

    Inheritance:
        ListView: Django BaseView for displaying a list of objects.
    """
    template_name = "orgs/list.html"
    model = Organization
    paginate_by=50

    def get_queryset(self) -> dict[str, Any]:
        """
        Filter the organizations by the diversity focus and optionally the location.

        TODO: #25 Make this support multiple diversity focuses.

        Returns:
            dict: QuerySet of organizations
        """
        diversity=DiversityFocus.objects.get(name__iexact=self.kwargs["diversity"])
        queryset = Organization.objects.filter(diversity_focus=diversity)
        if location:=self.request.GET.get('location', None):
            return queryset.filter(location=location) # Disconnect and filter by location
        return queryset

    def get_context_data(self, **kwargs) -> _context:
        """
        Custom context data for the view to pass into the template. 
        
        These are the tags that are being added:
            tag: The Diversity Focus object that was passed in the url
            focus: The focus tag of the view, which is 'diversity'
            map: switch to turn on the map view and request geodata from the API for the queryset.
                NOTE: there was an issue passing geojson directly to the template, so this is a workaround.
    `       AZURE_MAPS_KEY: The key for the Azure Maps API. See #18
            location: (Optional) The location passed into the request.
        """
        context = super().get_context_data(**kwargs)
        context["tag"] = DiversityFocus.objects.get(name__iexact=self.kwargs["diversity"])
        context['focus'] = 'diversity'
        context["map"] = f"{context['focus']}_focus={context['tag'].id}"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY

        if location:=self.request.GET.get('location', None):
            context["location"] = Location.objects.get(pk=location)
            context["map"] += f"&location={location}"
        
        return context

class TechnologyFocusView(ListView):
    """
    List of the technology focuses.

    Inheritance:
        ListView: Django BaseView for displaying a list of objects.
    """
    template_name = "tags/list.html"
    model = TechnologyFocus
    paginate_by=50

    def get_context_data(self, **kwargs) -> _context:
        """
        Add a focus and focus_filter to the context.
        This can be used to distinguish diversity focuses from other tags.
        """
        context = super().get_context_data(**kwargs)
        context["focus"] = "technology"
        context['focus_filter'] = 'technology_filter'
        return context
    

class TechnologyFocusFilterView(ListView):
    """
    List organizations based on the technology focus.

    Inheritance:
        ListView: Django BaseView for displaying a list of objects.
    """
    template_name = "orgs/list.html"
    model = Organization
    paginate_by: int = 25

    def get_queryset(self) -> dict[str, Any]:
        """
        Filter the organizations by the technology focus and optionally the location.

        Returns:
            object: QuerySet of organizations
        """
        orgs = Organization.objects.filter(technology_focus__name__iexact=self.kwargs["technology"])
        
        if location:=self.request.GET.get('location', None):
            return orgs.filter(location__pk=location)
        
        return orgs

    def get_context_data(self, **kwargs) -> _context:

        """
        Custom context data for the view to pass into the template. 

        NOTE: With most of this functionality being a duplicate of the DiversityFocusFilterView, a custom ViewClass could be DRYer solution.
        See #26
        """

        context = super().get_context_data(**kwargs)
        context["focus"] = "technology"
        context["tag"] = TechnologyFocus.objects.get(name__iexact=self.kwargs["technology"])
        context["map"] = f"{context['focus']}_focus={context['tag'].id}"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY


        if location:=self.kwargs.get('location', None):
            context["location"] = Location.objects.get(pk=location)
            context["map"] += f"&location={location}"
            
        return context


class OnlineDiversityFocusFilterView(ListView):
    """
    A filterview ListViews but for when the organization is online_only
    
    NOTE: This could inherit from the list view.

    """
    template_name = "orgs/list.html"
    model = Organization

    def get_queryset(self) -> dict[str, Any]:
        """Filter the organizations by the online_only and optionally the location."""
        return Organization.objects.filter(online_only=True).filter(diversity_focus=self.kwargs["diversity"])

    def get_context_data(self, **kwargs) -> _context:
        """Set the location to `Online`"""
        context = super().get_context_data(**kwargs)
        context["location"] = "Online"
        return context


class OnlineTechnologyFocusFilterView(ListView):
    """
    Like the OnlineDiversityFocusFilterView, but for the TechnologyFocusFilterView.

    NOTE: Both OnlineDiversity and OnlineTechnology FocusFilterViews could inherit from a singular CustomView.
    """
    template_name = "orgs/list.html"
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(diversity_focus=self.kwargs["technology"])

    def get_context_data(self, **kwargs) -> _context:
        """Set the location to `Online`"""
        context = super().get_context_data(**kwargs)
        context["location"] = "Online"
        return context
