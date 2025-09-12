# Trade-Customs-Analytics

## Problem Background
Customs administrations play a critical role in trade facilitation, revenue generation, and regulatory compliance. The efficiency and effectiveness of customs operations directly impact government revenue, international competitiveness, and compliance with trade laws. However, challenges such as data inconsistencies, uneven office performance, irregular tax declarations, and gaps in shipment monitoring often obscure the true state of customs performance.
To address these challenges, we need to analyze trade data across four critical dimensions: Import Volume and Value, Taxation and Revenue, Logistics and Shipment, and Compliance and Processing. Using real-world customs data, this project emphasizes not only technical data cleaning and visualization but also advanced statistical analysis and policy evaluation. The ultimate goal is to provide actionable insights that can support policymakers and stakeholders in improving customs efficiency, compliance monitoring, and revenue mobilization.  
## Problem Statement
Despite the availability of trade and customs data, decision-makers often face limited visibility into the relationships between trade values, taxation patterns, shipment logistics, and compliance risks. Current monitoring practices typically focus on revenue totals without adequate integration of other performance indicators, and this can lead to inefficiencies in customs operations, missed revenue opportunities, and challenges in ensuring fair and timely compliance.
There is therefore a need for a comprehensive, data-driven evaluation of customs performance that produces clear policy insights to strengthen trade governance.  
## Objectives
### Primary Objective
To conduct a comprehensive analysis of customs and trade data in order to uncover key patterns, relationships, and anomalies that can inform evidence-based decision-making and improve the efficiency and effectiveness of customs operations.

### Secondary Objectives
* To clean, validate, and prepare trade datasets for accurate and reliable analysis.
* To apply descriptive, exploratory, and statistical techniques in order to highlight major trends in import values, shipment flows, tax revenues, and compliance behaviors.
* To develop clear visualizations and policy-relevant insights through dashboards and reports.
* To assess the effectiveness of current tax structures and provide recommendations for potential improvements based on insights

## Data Description  
* Custom Office: The customs branch where the transaction was registered.
* Reg Number: Registration number of the import transaction.
* Importer: The importing entity or company responsible for the shipment.
* HS Code: Harmonized System code classifying the imported goods.
* FOB Value (N): Free on Board value, representing the cost of goods at the point of export (excluding shipping/insurance).
* CIF Value (N): Cost, Insurance, and Freight value, representing the total landed cost including shipping and insurance.
* Total Tax(N): The total duties, tariffs, and taxes paid on the transaction.
* Receipt Number: Official receipt reference for the tax payment.
* Receipt Date: The date the transaction was officially processed (76,493 valid entries, indicating some missing values).
* Mass(KG): Declared weight of the imported goods in kilograms.
* Country of Origin: The country where the goods were originally produced or manufactured.
* Country of Supply: The country to which the goods are being supplied
* Nbr of Containers: Number of shipping containers associated with the transaction.
* Container Nbr: Unique identifier for the shipping container.
* Container Size: Size category of the shipping container used.  
## Data Cleaning  
To prepare the dataset for analysis, several cleaning and transformation steps were applied to address missing values, inconsistencies, and formatting issues. The goal was to maintain data integrity while preserving all records, in line with the instruction not to drop any data.
### Handling Missing Values
* **Receipt Number & Receipt Date**: Missing Receipt Numbers were filled with "Unknown". Since all transactions with missing Receipt Numbers also had missing Receipt Dates, these dates were converted to proper datetime format, with missing values labeled as "NaT" (Not a Time).

* **Country of Supply**: A conditional imputation approach was applied. For each country, if it supplied goods to itself ≥70% of the time, then missing values were filled with the same country. For example, if Country of Origin = China and the supply records showed China supplied to itself at least 70% of the time, then missing Country of Supply entries were filled with "China". Otherwise, they were filled with "Unknown".

* **Container Information**:
    * If Number of Containers = 0, then Container Number and Container Size were labeled "Not Applicable".

    * If Number of Containers ≠ 0 but Container Number or Container Size was missing, they were filled with "Unknown".

### Corrections & Standardization

* **Number of Containers**:
    * Outlier values were corrected using importer records. For example, an unrealistic entry of 3248477 was changed to 1.
    * A non-numeric entry "W" was also replaced with 1 based on importer records.
* **Year Anomalies**: Receipt years dating back to 1866–1869 were identified These were mapped to recent years:
    * 1866 → 2021
    * 1867 → 2022
    * 1868 → 2023
    * 1869 → 2024
* **Data Type Standardization**:
    * Importer, HS Code were converted to string type for consistency.

**Outliers**
    * **Mass(KG)**: Several outlier values were observed (including zero or abnormally high weights). However, in accordance with guidance, no records were dropped or adjusted, since extreme values may highlight inefficiencies or unusual cases worth analyzing.  
## Descriptive Analysis
## Import Volume and Value
## Taxation and Revenue
## Logistics and Shipment
## Compliance and Processing
* Some offices like HM CARGO and NT registred more share of the total registered imports
* Others like UA PORT, NT_2, LC, RP_1, DK_COLLECTION, and RW PORT had less than 1% of the total registered imports
* But then, the companies who registered less than 1% of the total shipments, among the top 6 with high average tax amounts
* It's possible that might be because some specialized products pass through these places and are highly taxed
* And custom offices through which most of the shipments passed through, had a much lower average tax amount
* What happened was the goods cleared in those offices, were heavily taxed
* Unfortunately, the products that were mostly processed in these offices, were not the ones that incurred the most task, showing that it's just some products that were heavily taxed.
* What was causing this, could it be the mass? The mass has very extreme outliers, probably it's those outlier masses were incurring the high taxes
* While generally, products with lower masses still incured high taxes, For these particular offices, most of them had very high average masses.
* There is a theory here:
    * The policies in some of these places are different and the taxes incurred actually depends on the mass of the product, which could possibly be a compliance issue

* Some custom offices also recorded zero (0) mass, which could be pointing to processing efficiency issues, since products can have masses close to zero not actually a zero mass

## Advanced Statistical Analysis

* FOB and CIF have a perfect 1.0 correlation, which is expected
* CIF vs Total Tax has a strong positive correlation of 0.72, and FOB vs Total Tax also has a strong correlation of 0.71, suggesting that tax is largely driven by the value of goods.
* Mass and Tax have a very weak correlation, suggesting that mass doesn't explain tax.
* Overall, Tax seems to be levied based on the value of the product, not the weight
* Due to the multicollinearity of the FOB value and the CIF value, the CIF value was chosen for further analysis, since it includes the FOB value also.
* Then, did a Reression analysis between the CIF value and the Total tax. It showed a R-squared value of 0.521, showing that only about 52.1% of variation in tax can be explained by CIF value
* The Coefficient of the CIF value is approx. 0.095, showing that for every #1 increase in the CIF value, tax increases by #0.095, in simple words, approximately 9.5% of the CIF alue is taken as tax.
* Model also shows a baseline charge of about #881,900 even at a CFI value = 0
* Also did a regression analysis betwen the Mass and the Tax. The R-squared value shows that only 2.8% of taxes could be explained by the mass, showing that the mass isn't a major factor that drives tax incurred.
* A regression plot between the CIF value and the total tax shows that there is indeed a positive correlation between both. Different layers could be seen as well, which could probably point to the fact that the rate at which tax is incurred differs probably by country of supply
* Further Analysis between the CIF value and taxes for each custom office, shows that all offices to some degree, charge taxes based on the value of the product.
* The same was also done for the countries of supply and countries like UAE, India, Swaziland, Switzerland didn't follow that policy, especially the British Virgin Islands, which seemed to completely follow a different trajectory (policy) different from all others.

## Trend Analysis showing Seasonality or Periodic Trends in Trade Volume
## Analytical Skills
## Recommendations
## Conclusion