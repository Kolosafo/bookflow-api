from .models import MainArgument, Framework, FrameworkComponent, KeyInsight, ImplementationGuide, ImplementationStep, ImplementationMeta, OnePageSummary, BookAnalysisResponse

def save_book_analysis(data, title, author, book_id):
    """
    View to save book analysis data into BookAnalysisResponse model.
    
    Expects JSON payload with the structure from your document.
    """
    try:
        
        # Extract top-level info (you may want to pass these separately)
        book_title = title
        
        # 1. Create MainArgument
        main_arg_data = data.get('main_argument', {})
        main_argument = MainArgument.objects.create(
            problem_identified=main_arg_data.get('problem_identified', ''),
            solution_proposed=main_arg_data.get('solution_proposed', ''),
            why_it_matters=main_arg_data.get('why_it_matters', '')
        )
        
        # 2. Create Framework and its components
        framework_data = data.get('framework', {})
        framework = None
        if framework_data:
            framework = Framework.objects.create(
                name=framework_data.get('name', ''),
                overview=framework_data.get('overview', ''),
                visual_representation=framework_data.get('visual_representation')
            )
            
            # Create FrameworkComponents
            for component_data in framework_data.get('components', []):
                FrameworkComponent.objects.create(
                    framework=framework,
                    name=component_data.get('name', ''),
                    description=component_data.get('description', ''),
                    example=component_data.get('example', '')
                )
        
        # 3. Create KeyInsights (ManyToMany, so we'll collect them)
        key_insights = []
        for insight_data in data.get('key_insights', []):
            insight = KeyInsight.objects.create(
                title=insight_data.get('title', ''),
                description=insight_data.get('description', ''),
                theme=insight_data.get('theme', 'other'),
                practical_application=insight_data.get('practical_application', ''),
                supporting_quote=insight_data.get('supporting_quote')
            )
            key_insights.append(insight)
        
        # 4. Create ImplementationGuide with steps and meta
        impl_guide_data = data.get('implementation_guide', {})
        implementation_guide = ImplementationGuide.objects.create(
            overview=impl_guide_data.get('overview', '')
        )
        
        # Create ImplementationSteps
        for step_data in impl_guide_data.get('steps', []):
            ImplementationStep.objects.create(
                guide=implementation_guide,
                step_number=step_data.get('step_number', 0),
                title=step_data.get('title', ''),
                description=step_data.get('description', ''),
                time_estimate=step_data.get('time_estimate'),
                resources_needed=step_data.get('resources_needed', []),
                success_criteria=step_data.get('success_criteria', '')
            )
        
        # Create ImplementationMeta
        ImplementationMeta.objects.create(
            guide=implementation_guide,
            common_pitfalls=impl_guide_data.get('common_pitfalls', []),
            quick_wins=impl_guide_data.get('quick_wins', [])
        )
        
        # 5. Create OnePageSummary
        summary_data = data.get('one_page_summary', {})
        one_page_summary = OnePageSummary.objects.create(
            headline=summary_data.get('headline', ''),
            core_message=summary_data.get('core_message', ''),
            key_principles=summary_data.get('key_principles', []),
            actionable_takeaways=summary_data.get('actionable_takeaways', []),
            memorable_quote=summary_data.get('memorable_quote', ''),
            who_should_read=summary_data.get('who_should_read', ''),
            bottom_line=summary_data.get('bottom_line', '')
        )
        
        # 6. Create BookAnalysisResponse (top-level)
        book_analysis = BookAnalysisResponse.objects.create(
            book_id = book_id,
            book_title=book_title,
            book_author=author,
            main_argument=main_argument,
            framework=framework,
            implementation_guide=implementation_guide,
            one_page_summary=one_page_summary
        )
        
        # Add ManyToMany relationships
        book_analysis.key_insights.set(key_insights)
        
        
        
    except Exception as E:
        print("NO SAVER: ", E)
        return None

