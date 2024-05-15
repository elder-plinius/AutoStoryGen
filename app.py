import streamlit as st
from gemini_chat import GeminiChat
import io

def download_story(full_story):
    buffer = io.BytesIO()
    buffer.write(full_story.encode('utf-8'))
    buffer.seek(0)
    return buffer

def main():
    st.title("Agentic Story Generator")

    # Initialize GeminiChat agent
    gemini_chat = GeminiChat()

    # User input for story variables
    subreddit_or_community = st.text_input("Subreddit/Community:")
    story_title = st.text_input("Story Title:")
    story_concept = st.text_input("Story Concept:")
    niche_genre = st.text_input("Niche/Genre:")
    desired_word_count = st.number_input("Target Word Count:", min_value=1, step=1)
    num_chapters = st.number_input("Number of Chapters:", min_value=1, step=1)

    st.write("Recommendation: Aim for approximately 500 words per chapter.")

    if st.button("Generate Outline"):
        # Variable validation
        missing_variables = []
        if not subreddit_or_community:
            missing_variables.append("subreddit/community")
        if not story_title:
            missing_variables.append("story title")
        if not story_concept:
            missing_variables.append("story concept")
        if not niche_genre:
            missing_variables.append("niche/genre")
        if not desired_word_count:
            missing_variables.append("target word count")
        if not num_chapters:
            missing_variables.append("number of chapters")

        if missing_variables:
            # Ask Gemini to fill out the missing variables autonomously
            missing_variable_prompt = f"""
            [System Prompt]
            The user has not provided the following story variables: {', '.join(missing_variables)}. Please fill out these variables autonomously, taking your best educated guess based on the available information and best practices for creative storywriting.
            [End System Prompt]

            [Prompt Template]
            🌟 Story Variables
            * Subreddit/Community: {subreddit_or_community}
            * Story Title: {story_title}
            * Story Concept: {story_concept}
            * Niche/Genre: {niche_genre}
            * Target Word Count: {desired_word_count}
            * Number of Chapters: {num_chapters}

            Please provide your autonomous suggestions for the missing variables, keeping in mind the principles of engaging storytelling, coherent narrative structure, and well-developed characters and themes:
            """
            missing_variable_response = gemini_chat.send_message(missing_variable_prompt)
            st.write("Gemini's Autonomous Suggestions:")
            st.write(missing_variable_response)

            # Update the story variables based on Gemini's suggestions
            # Modify this part based on the actual format of Gemini's response
            try:
                updated_variables = missing_variable_response.split("\n")
                for variable in updated_variables:
                    if ":" in variable:
                        key, value = variable.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "Subreddit/Community":
                            subreddit_or_community = value
                        elif key == "Story Title":
                            story_title = value
                        elif key == "Story Concept":
                            story_concept = value
                        elif key == "Niche/Genre":
                            niche_genre = value
                        elif key == "Target Word Count":
                            desired_word_count = int(value)
                        elif key == "Number of Chapters":
                            num_chapters = int(value)
            except Exception as e:
                st.warning(f"Failed to parse Gemini's response. Error: {str(e)}")

        # Generate story outline
        outline_prompt = f"""
        [System Prompt]
        You are an AI story outliner. Your task is to generate a compelling and detailed story outline based on the provided story variables and the prompt template, incorporating best practices for creative storywriting.
        [End System Prompt]

        [Prompt Template]
        🌟 Story Variables
        * Subreddit/Community: {subreddit_or_community}
        * Story Title: {story_title}
        * Story Concept: {story_concept}
        * Niche/Genre: {niche_genre}
        * Target Word Count: {desired_word_count}
        * Number of Chapters: {num_chapters}

        Please generate a captivating story outline that includes the following elements, ensuring a well-structured narrative arc, engaging characters, immersive settings, and thought-provoking themes:
        1. Story Arc:
           * Exposition: Set the stage, introduce the main characters, and establish the initial conflict or inciting incident.
           * Rising Action: Develop the conflict, introduce complications, and raise the stakes for the characters.
           * Climax: Present the turning point or moment of highest tension, where the characters face the ultimate challenge or make crucial decisions.
           * Falling Action: Show the consequences of the climax and how the characters deal with the aftermath.
           * Resolution: Provide a satisfying conclusion that ties up loose ends, resolves character arcs, and leaves a lasting impact on the reader.
        2. Chapter Summaries: Briefly describe the main events, revelations, and character developments in each chapter, ensuring a coherent and engaging flow of the narrative.
        3. Character Profiles: Create well-rounded and relatable characters with distinct personalities, motivations, and growth arcs throughout the story.
        4. Setting Descriptions: Vividly depict the story's settings, immersing the reader in the world and atmosphere you've created.
        5. Themes and Motifs: Weave meaningful themes and recurring motifs into the story, adding depth and resonance to the narrative.
        6. Conflict and Stakes: Craft compelling conflicts, both internal and external, that challenge the characters and keep the reader invested in the story's outcome.
        [End Prompt Template]
        """
        outline_response = gemini_chat.send_message(outline_prompt)
        st.session_state.outline_response = outline_response
        st.write("Story Outline:")
        st.write(outline_response)
    else:
        outline_response = st.session_state.get("outline_response", "")

    if outline_response:
        if "story_parts" not in st.session_state:
            # Display Approve Outline and Request Improvements buttons
            if st.button("Approve Outline and Generate Story"):
                # Generate story parts
                story_parts = []
                for chapter in range(1, int(num_chapters) + 1):
                    story_prompt = f"""
                    [System Prompt]
                    You are an AI story writer. Your task is to generate an engaging and immersive chapter based on the provided story outline and the prompt template, incorporating best practices for creative storywriting.
                    [End System Prompt]

                    [Prompt Template]
                    Please generate Chapter {chapter} of the story based on the following outline:
                    {outline_response}

                    Ensure that the chapter:
                    - Follows the story arc and advances the plot in a meaningful way
                    - Develops the characters, showcasing their personalities, motivations, and growth
                    - Immerses the reader in the story's settings through vivid descriptions and sensory details
                    - Explores the themes and motifs established in the outline
                    - Creates engaging dialogue that reveals character dynamics and moves the story forward
                    - Builds tension, suspense, or emotional resonance as appropriate for the genre and story beats
                    - Maintains a consistent tone and style that aligns with the target audience and niche
                    [End Prompt Template]
                    """
                    part_response = gemini_chat.send_message(story_prompt)
                    story_parts.append(part_response)
                    st.write(f"Chapter {chapter} generated.")

                # Combine story parts
                full_story = "\n".join(story_parts)
                st.session_state.story_parts = story_parts
                st.session_state.full_story = full_story

            if st.button("Request Improvements"):
                st.session_state.requesting_improvements = True

        if "requesting_improvements" in st.session_state and st.session_state.requesting_improvements:
            # Display feedback input field and Submit Feedback button
            user_feedback = st.text_input("Please provide feedback on the outline:")

            if st.button("Submit Feedback"):
                # Request improvements to the outline
                improvement_prompt = f"""
                [System Prompt]
                The user has requested improvements to the story outline. Please provide an updated outline based on their feedback, incorporating best practices for creative storywriting.
                [End System Prompt]

                [Prompt Template]
                Original Outline:
                {outline_response}

                User Feedback:
                {user_feedback}

                Please generate an improved story outline that:
                - Addresses the user's feedback and concerns
                - Enhances the story arc, character development, settings, themes, and conflicts
                - Ensures a cohesive and engaging narrative flow
                - Adheres to the story variables and genre conventions
                - Incorporates best practices for creative storywriting, such as show-don't-tell, meaningful symbolism, and evocative language
                [End Prompt Template]
                """
                improved_outline = gemini_chat.send_message(improvement_prompt)
                st.session_state.outline_response = improved_outline
                st.write("Improved Story Outline:")
                st.write(improved_outline)

                # Reset requesting improvements state
                st.session_state.requesting_improvements = False

        if "story_parts" in st.session_state:
            # Display generated story parts and full story
            st.write("Generated Story Parts:")
            for i, part in enumerate(st.session_state.story_parts):
                st.write(f"Chapter {i + 1}:")
                st.write(part)

            st.write("Full Story:")
            st.write(st.session_state.full_story)

            buffer = download_story(st.session_state.full_story)
            st.download_button(
                label="Download Story",
                data=buffer,
                file_name="generated_story.txt",
                mime="text/plain"
            )

            # Display Restart button
            if st.button("Restart"):
                # Clear session state and rerun the app
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.experimental_rerun()

if __name__ == "__main__":
    main()
