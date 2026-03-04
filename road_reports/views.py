from django.shortcuts import render
from django.conf import settings

from .forms import UploadExcelForm
from .services.excel_service import read_and_validate_excel, calculate_total_length
from .services.word_service import (
    build_word_report,
    save_document,
    generate_report_filename,
)
from .services.ai_service import generate_road_summary


def upload_excel(request):
    total_length = None
    error = None
    download_url = None

    if request.method == "POST":
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]

            allowed_types = {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
            }

            if excel_file.content_type not in allowed_types:
                error = "Можно загружать только Excel-файлы .xlsx"
                return render(request, "road_reports/upload.html", {"form": form, "error": error})

            try:
                df = read_and_validate_excel(excel_file)
                total_length = calculate_total_length(df)
                summary = generate_road_summary(df, total_length)

                document = build_word_report(df, total_length, summary)

                file_name = generate_report_filename(excel_file.name)
                save_document(document, str(settings.MEDIA_ROOT), file_name)
                download_url = settings.MEDIA_URL + file_name

            except ValueError as e:
                error = str(e)
            except Exception as e:
                error = f"Ошибка при обработке файла: {e}"
    else:
        form = UploadExcelForm()

    return render(
        request,
        "road_reports/upload.html",
        {
            "form": form,
            "total_length": total_length,
            "error": error,
            "download_url": download_url,
        },
    )