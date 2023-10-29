import pandas as pd
import discogs_client as dc
from authenticate import authenticate

d = authenticate()

df = pd.read_csv("collection//Book1.csv", encoding='utf-8-sig')

# print(df)


for index, row in df.iterrows():
    release_id = str(int(row.release_id))
    result = d.release(release_id)
    try:
        img_url = result.images[0]['resource_url']
        df.at[index,'img_url'] = img_url
        print(df.loc[index])
    except(AttributeError):
        print("no image")
    except(TypeError):
        print("wrong type")

    


    # img_url = result.master.images[0]['resource_url']
    # print(img_url)

    # df[df.img_url] = str(result.master.images[0]['resource_url'])
    # result_test = "test fill" + str(index)
    # df[df.img_url] = str(result.master.images[0]['resource_url'])
    # df[index]['img_url'] = result.master.images[0]['resource_url']
    # print(df)

print(df)
df.to_csv('output_test.csv')




# df_ids = df["release_id"].tolist()

# print(df_ids)

