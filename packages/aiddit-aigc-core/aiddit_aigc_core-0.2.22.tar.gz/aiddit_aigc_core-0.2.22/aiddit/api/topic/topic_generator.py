from tenacity import retry, stop_after_attempt, wait_fixed

from aiddit.api.xhs_api import _get_xhs_account_info, _get_xhs_account_note_list, _get_note_detail_by_id
import aiddit.api.topic.prompt as prompt
import aiddit.model.google_genai as google_genai
import aiddit.utils as utils
from aiddit.model.google_genai import GenaiConversationMessage, GenaiMessagePart, MessageType
import os
import aiddit.api.history_note as history_note


def reference_note_available(xhs_user_id: str, reference_note_id: str):
    account_info = _get_xhs_account_info(xhs_user_id)
    account_history_note_path = _get_xhs_account_note_list(xhs_user_id)

    model = google_genai.MODEL_GEMINI_2_5_FLASH

    reference_note = _get_note_detail_by_id(reference_note_id)

    history_notes = utils.load_from_json_dir(account_history_note_path)

    history_messages = []

    history_messages.extend(history_note.build_history_note_messages(history_notes))

    # 参考帖子
    if reference_note.get("content_type") == "video" and reference_note.get("video", {}).get("video_url") is not None:
        reference_note_medias = [reference_note.get("video", {}).get("video_url")]
    else:
        reference_note_medias = [utils.oss_resize_image(i) for i in
                                 utils.remove_duplicates(reference_note.get("images"))]
    reference_note_prompt = prompt.REFERENCE_NOTE_PROVIDER_PROMPT.format(
        title=reference_note.get("title"),
        body_text=reference_note.get("body_text"),
        image_count=len(reference_note_medias)
    )
    reference_note_conversation_user_message = google_genai.GenaiConversationMessage.text_and_images(
        reference_note_prompt, reference_note_medias)
    history_messages.append(reference_note_conversation_user_message)

    # 获取当前文件的目录
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    print("current_file_dir ---", current_file_dir)
    # 专家知识
    expert_knowledge_path = os.path.join(current_file_dir, "../expert/topic_theory_expert.txt")
    print("expert_knowledge_path ---", expert_knowledge_path)

    if os.path.exists(expert_knowledge_path):
        expert_knowledge_conversation_user_message = google_genai.GenaiConversationMessage.text_and_images(
            f"小红书内容创作的理论基石：基于特定账号人设与参考帖子的选题策略。从中你可以学习 了解小红书内容创作的理论基石，基于特定账号人设与参考帖子的选题策略。",
            expert_knowledge_path)
        history_messages.append(expert_knowledge_conversation_user_message)
    else:
        print("expert_knowledge_path not exist , skip expert knowledge")

    # 参考帖子是否能产生选题
    reference_available_prompt = prompt.REFERENCE_NOTE_AVAILABLE_PROMPT.format(
        account_name=account_info.get("account_name"),
        account_description=account_info.get("description"), )
    reference_available_conversation_user_message = GenaiConversationMessage.one("user",
                                                                                 reference_available_prompt)

    system_prompt_count = google_genai.google_genai_client.models.count_tokens(model=model,contents=prompt.SYSTEM_INSTRUCTION_PROMPT)
    print("system_prompt_count ---", system_prompt_count)

    script_ans_conversation_model_message = google_genai.google_genai_output_images_and_text(
        reference_available_conversation_user_message,
        model=model,
        history_messages=history_messages,
        system_instruction_prompt=prompt.SYSTEM_INSTRUCTION_PROMPT)
    ans_content = script_ans_conversation_model_message.content[0].value

    return ans_content, [script_ans_conversation_model_message.usage_metadata]


if __name__ == "__main__":
    ans, usage = reference_note_available("56e02fa4cb35fb071599c959", "682d78b1000000002100468f")

    print(usage)
    pass
