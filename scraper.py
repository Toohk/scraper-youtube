
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import os

def get_video_id_from_title(search_query, it):
    # Initialiser le driver Chrome en mode sans tête
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    # URL de la recherche YouTube
    url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

    try:
        driver.get(url)
        driver.implicitly_wait(10)
        video_duration_elements = driver.find_elements(By.CSS_SELECTOR, 'span.style-scope.ytd-thumbnail-overlay-time-status-renderer')
        video_id_elements = driver.find_elements(By.CSS_SELECTOR, 'a#video-title')

        if video_duration_elements and video_id_elements:
            for i in range(min(3, len(video_duration_elements))):
                video_duration = video_duration_elements[i].text
                video_url = video_id_elements[i].get_attribute('href')
                video_id = re.search(r'v=([\w-]+)', video_url).group(1) if video_url and re.search(r'v=([\w-]+)', video_url) else "ID non trouvé"

                time_parts = video_duration.split(':')
                total_seconds = int(time_parts[0]) * 60 + int(time_parts[1])

                if total_seconds < 280:
                    print(f"Numéro de l'itération: {it}")
                    return video_id
        else:
            return "Aucune vidéo trouvée"
    except Exception as e:
        return f"Une erreur est survenue : {e}"
    finally:
        driver.quit()



def update_csv(input_file, output_file, progress_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['video_id']

        # Chargez le dernier index sauvegardé, s'il existe
        last_saved_index = -1
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as prog_file:
                last_saved_index = int(prog_file.read())

        # Lire toutes les lignes dans une liste
        all_rows = list(reader)
        
        # Écrire seulement les lignes jusqu'au dernier index sauvegardé dans le fichier de sortie
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            # Écrivez les en-têtes
            writer.writeheader()
            
            for index in range(min(len(all_rows), last_saved_index+1)):
                writer.writerow(all_rows[index])

        # Continuez à partir du dernier index sauvegardé
        with open(output_file, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            for index in range(last_saved_index+1, len(all_rows)):
                title = all_rows[index]['title']
                video_id = get_video_id_from_title(title + " opening", index)
                all_rows[index]['video_id'] = video_id
                writer.writerow(all_rows[index])

                if (index + 1) % 10 == 0:
                    outfile.flush()
                    # Sauvegardez l'index actuel dans le fichier de progrès
                    with open(progress_file, 'w') as prog_file:
                        prog_file.write(str(index))
                    print(f"Les données ont été sauvegardées après {index + 1} itérations")
# Chemin vers votre fichier CSV d'entrée et de sortie
input_file = './AnimeList_with_only_titles.csv'
output_file = './output.csv'
progress_file = './progress.txt'

update_csv(input_file, output_file, progress_file)

